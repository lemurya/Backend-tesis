import os
import torch
import torch.nn as nn
from transformers import ViTModel
from torchvision import transforms
from PIL import Image

from app.database import SessionLocal
from app.config import settings
from app.crud import get_estilos

# ------------------ TRIPLET ATTENTION ------------------
class TripletAttention(nn.Module):
    def __init__(self, in_channels, kernel_size=7):
        super(TripletAttention, self).__init__()
        padding = (kernel_size - 1) // 2
        self.spatial_conv = nn.Conv2d(in_channels, in_channels, kernel_size,
                                      padding=padding, bias=False)
        self.channel_conv = nn.Conv2d(in_channels, in_channels, kernel_size=1, bias=False)

    def forward(self, x):
        spatial_attn = torch.sigmoid(self.spatial_conv(x))
        channel_attn = torch.sigmoid(self.channel_conv(x))
        return x * spatial_attn * channel_attn

# ------------------ VIT IMPROVED ------------------
class ViTImprovedHuggingface(nn.Module):
    def __init__(self, num_classes, model_name="google/vit-base-patch16-224", drop_rate=0.5):
        super(ViTImprovedHuggingface, self).__init__()
        self.vit = ViTModel.from_pretrained(model_name)
        self.hidden_dim = self.vit.config.hidden_size  # e.g., 768
        self.num_patches = 196
        self.grid_size = int(self.num_patches ** 0.5)
        self.triplet_attention = TripletAttention(in_channels=self.hidden_dim, kernel_size=7)
        self.dropout = nn.Dropout(drop_rate) if drop_rate > 0 else nn.Identity()
        self.classifier = nn.Linear(self.hidden_dim * 2, num_classes)

    def forward(self, x):
        outputs = self.vit(x)
        last_hidden_state = outputs.last_hidden_state
        class_token = last_hidden_state[:, 0, :]
        patch_tokens = last_hidden_state[:, 1:, :]
        B, N, C = patch_tokens.shape
        patch_tokens = patch_tokens.transpose(1, 2).reshape(B, C, self.grid_size, self.grid_size)
        patch_attended = self.triplet_attention(patch_tokens)
        patch_pooled = patch_attended.mean(dim=[2, 3])
        combined = torch.cat([class_token, patch_pooled], dim=1)
        combined = self.dropout(combined)
        logits = self.classifier(combined)
        return logits

# Device and transform
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.5] * 3, std=[0.5] * 3)
    ])


def init_model(num_classes: int):
    """
    Inicializa y carga el modelo con los pesos configurados en settings.model_path
    """
    global model
    model = ViTImprovedHuggingface(num_classes=num_classes)
    model.load_state_dict(torch.load(settings.model_path, map_location= device))
    model.eval()

def predict_style_from_path(path: str):
    """
    Ejecuta inferencia en `path`, recupera todos los estilos de BD,
    construye scores y devuelve el estilo con mayor probabilidad.
    """
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Imagen no encontrada: {path}")

    img = Image.open(path).convert("RGB")
    input_tensor = transform(img).unsqueeze(0)

    CLASSES = [
        "Byzantin_Iconography",
        "Early_Renaissance",
        "Northern_Renaissance",
        "High_Renaissance",
        "Baroque",
        "Rococo",
        "Romanticism",
        "Realism",
        "Impressionism",
        "Post_Impressionism",
        "Expressionism",
        "Symbolism",
        "Fauvism",
        "Cubism",
        "Surrealism",
        "NaiveArt",
        "PopArt"
    ]
    with torch.no_grad():
        output = model(input_tensor)
        predicted_class = torch.argmax(output, dim=1).item()

    predicted = CLASSES[predicted_class]

    print(predicted)

    return predicted
