from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Configuración de la aplicación, cargada desde variables de entorno o archivo .env.
    Atributos:
      - database_url: URL de la base de datos.
      - model_path: Ruta al archivo de pesos del modelo entrenado.
    """
    database_url: str                  # lee de env DATABASE_URL
    model_path:   str                  # lee de env MODEL_PATH

    # Configuración para pydantic-settings
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
    )

settings = Settings()
