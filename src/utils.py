from skimage import img_as_ubyte, io
from skimage.color import rgb2gray, gray2rgb
import streamlit as st

def normalizar_imagen(imagen, modo_objetivo='RGB'):
    """
    Normaliza el modo de color de una imagen.
    """
    if modo_objetivo == 'RGB' and len(imagen.shape) == 2:
        # Convierte imágenes en escala de grises a RGB
        return gray2rgb(imagen)
    elif modo_objetivo == 'L' and len(imagen.shape) == 3:
        # Convierte imágenes RGB a escala de grises
        return rgb2gray(imagen)
    return imagen

def guardar_imagen(imagen, nombre_archivo):
    """
    Guarda la imagen asegurando que se preserve la información correctamente.
    """
    # Asegurar que la imagen esté en uint8
    imagen_a_guardar = img_as_ubyte(imagen)
    io.imsave(nombre_archivo, imagen_a_guardar)

def cargar_imagen(archivo):
    """
    Carga la imagen asegurando la correcta interpretación del formato.
    """
    # Leer la imagen directamente desde el archivo usando skimage
    imagen = io.imread(archivo)
    return imagen

def mostrar_metricas(metricas, titulo="Métricas de Calidad", bits_usados=None):
    """
    Muestra las métricas en Streamlit.
    """
    st.write(f"### {titulo}")
    
    for metrica, valor in metricas.items():
        st.write(f"{metrica}: {valor:.4f}")
    
    psnr = metricas['PSNR']
    if bits_usados is not None:
        if psnr > 40:
            st.success("🟢 Calidad Excelente - La imagen es prácticamente idéntica al original.")
        elif psnr > 30:
            st.info("🟡 Buena Calidad - Hay algunas diferencias menores pero aceptable.")
        elif psnr > 20:
            st.warning("🟠 Calidad Regular - Hay diferencias notables pero la imagen es reconocible.")
        else:
            st.error("🔴 Calidad Baja - La imagen recuperada tiene diferencias significativas.")