
# Run Project

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload




#

CREATE TABLE public.estilos (
    id integer,
    nombre text,
    descripcion text,
    tecnicas text
);




CREATE TABLE public.history (
    id SERIAL PRIMARY KEY,
    estilo_id INTEGER NOT NULL,
    image_path TEXT,
    confidence_score DECIMAL(5,4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    client_ip TEXT,
    user_agent TEXT,
    
    -- Foreign key a la tabla estilos
    FOREIGN KEY (estilo_id) REFERENCES public.estilos(id) ON DELETE CASCADE
);

-- Crear índices para mejorar el rendimiento
CREATE INDEX idx_history_estilo_id ON public.history(estilo_id);
CREATE INDEX idx_history_created_at ON public.history(created_at);

-- Opcional: Crear una vista para consultas comunes
CREATE VIEW v_history_with_estilos AS
SELECT 
    h.id,
    h.estilo_id,
    e.nombre as estilo_nombre,
    e.descripcion as estilo_descripcion,
    h.image_path,
    h.confidence_score,
    h.created_at,
    h.client_ip,
    h.user_agent
FROM public.history h
JOIN public.estilos e ON h.estilo_id = e.id
ORDER BY h.created_at DESC;



SELECT id, estilo_id, image_path, confidence_score, created_at, client_ip, user_agent
	FROM public.history;

DROP VIEW IF EXISTS v_history_with_estilos;

CREATE VIEW v_history_with_estilos AS
SELECT 
    h.id,
    h.estilo_id,
    e.nombre as estilo_nombre,
    e.descripcion as estilo_descripcion,
    h.image_path,
    h.confidence_score,
    h.created_at,
    h.client_ip,
    h.user_agent
FROM public.history h
JOIN public.estilos e ON h.estilo_id = e.id
ORDER BY h.created_at DESC;