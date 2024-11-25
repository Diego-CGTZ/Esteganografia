from skimage import img_as_float, img_as_ubyte, io
from skimage.color import rgb2gray, gray2rgb
import numpy as np
import streamlit as st

def normalize_image(image, target_mode='RGB'):
    """
    Normaliza el modo de color de una imagen.
    """
    if target_mode == 'RGB' and len(image.shape) == 2:
        # Convierte imágenes en escala de grises a RGB
        return gray2rgb(image)
    elif target_mode == 'L' and len(image.shape) == 3:
        # Convierte imágenes RGB a escala de grises
        return rgb2gray(image)
    return image


def calculate_metrics(original, recovered):
    """
    Calcula métricas de error entre dos imágenes.
    """
    original = img_as_float(original)
    recovered = img_as_float(recovered)
    
    mse = np.mean((original - recovered) ** 2)
    if mse == 0:
        psnr = float('inf')
    else:
        psnr = 20 * np.log10(1.0 / np.sqrt(mse))
    
    return {
        'MSE': mse,
        'PSNR': psnr
    }

def display_metrics(metrics, title="Métricas de Calidad", bits_used=None):
    """
    Muestra las métricas en Streamlit.
    """
    st.write(f"### {title}")
    
    for metric, value in metrics.items():
        st.write(f"{metric}: {value:.4f}")
    
    psnr = metrics['PSNR']
    if bits_used is not None:
        if bits_used >= 6:
            st.success("🟢 Calidad Excelente - Se utilizaron suficientes bits para una recuperación casi perfecta.")
        elif bits_used >= 4:
            st.info("🟡 Buena Calidad - Se puede recuperar bastante detalle.")
        elif bits_used >= 2:
            st.warning("🟠 Calidad Regular - La calidad es limitada, pero la imagen es reconocible.")
        else:
            st.error("🔴 Calidad Baja - Muy pocos bits utilizados, la calidad de la imagen es pobre.")
    else:
        if psnr > 40:
            st.success("🟢 Calidad Excelente - La imagen es prácticamente idéntica al original.")
        elif psnr > 30:
            st.info("🟡 Buena Calidad - Hay algunas diferencias menores pero aceptable.")
        elif psnr > 20:
            st.warning("🟠 Calidad Regular - Hay diferencias notables pero la imagen es reconocible.")
        else:
            st.error("🔴 Calidad Baja - La imagen recuperada tiene diferencias significativas.")

def hide_image(cover_image, secret_image, bits):
    """
    Oculta una imagen en otra usando LSB.
    """
    # Asegurar que las imágenes sean uint8
    cover = img_as_ubyte(cover_image.copy())
    secret = img_as_ubyte(secret_image.copy())
    
    # Crear máscaras
    mask_cover = 256 - (2**bits)
    mask_secret = 2**bits - 1
    
    # Limpiar los LSB de la imagen de portada
    cover_cleared = cover & mask_cover
    
    # Preparar los bits de la imagen secreta
    secret_bits = (secret >> (8 - bits)) & mask_secret
    
    # Combinar las imágenes
    stego = cover_cleared | secret_bits
    
    return stego

def extract_image(stego_image, bits, output_mode='RGB'):
    """
    Extrae la imagen oculta.
    """
    # Asegurar que la imagen esté en uint8
    stego = img_as_ubyte(stego_image.copy())
    
    # Crear máscara para extraer los LSB
    mask = 2**bits - 1
    
    # Extraer los bits ocultos
    extracted = (stego & mask)
    
    # Escalar los valores extraídos al rango completo
    extracted = (extracted << (8 - bits))
    
    # Convertir al modo de color deseado si es necesario
    if output_mode == 'L' and len(extracted.shape) == 3:
        extracted = rgb2gray(extracted)
    elif output_mode == 'RGB' and len(extracted.shape) == 2:
        extracted = gray2rgb(extracted)
    
    return extracted

def save_image(image, filename):
    """
    Guarda la imagen asegurando que se preserve la información correctamente.
    """
    # Asegurar que la imagen esté en uint8
    image_to_save = img_as_ubyte(image)
    io.imsave(filename, image_to_save)

def load_image(file):
    """
    Carga la imagen asegurando la correcta interpretación del formato.
    """
    # Leer la imagen directamente desde el archivo usando skimage
    image = io.imread(file)
    return image

# Interfaz de Streamlit
st.title('Esteganografía de Imágenes')

tab1, tab2 = st.tabs(["Ocultar Imagen", "Extraer Imagen"])

with tab1:
    st.header("Ocultar una imagen")
    
    bits_hide = st.slider('Número de bits a utilizar (LSB)', 1, 8, 1, key='hide_bits',
                         help='Más bits = mejor calidad de la imagen oculta, pero más visible')
    
    cover_file = st.file_uploader("Selecciona la imagen de portada", type=['png', 'jpg', 'jpeg'], key='cover')
    secret_file = st.file_uploader("Selecciona la imagen a ocultar", type=['png', 'jpg', 'jpeg'], key='secret')
    
    if cover_file and secret_file:
        try:
            # Cargar imágenes usando la nueva función
            cover_image = load_image(cover_file)
            secret_image = load_image(secret_file)
            
            # Asegurar que las imágenes estén en RGB
            cover_image = normalize_image(cover_image, 'RGB')
            secret_image = normalize_image(secret_image, 'RGB')
            
            # Ajustar tamaños
            min_height = min(cover_image.shape[0], secret_image.shape[0])
            min_width = min(cover_image.shape[1], secret_image.shape[1])
            cover_image = cover_image[:min_height, :min_width]
            secret_image = secret_image[:min_height, :min_width]
            
            col1, col2 = st.columns(2)
            with col1:
                st.image(cover_image, caption="Imagen de portada")
                st.write(f"Dimensiones: {cover_image.shape[:2]}")
            with col2:
                st.image(secret_image, caption="Imagen a ocultar")
                st.write(f"Dimensiones: {secret_image.shape[:2]}")
            
            if st.button("Ocultar Imagen"):
                stego_image = hide_image(cover_image, secret_image, bits_hide)
                metrics_cover = calculate_metrics(cover_image, stego_image)
                
                st.image(stego_image, caption="Imagen con mensaje oculto")
                display_metrics(metrics_cover, "Métricas de calidad - Imagen de portada", bits_hide)
                
                # Guardar la imagen en formato PNG
                output_filename = "stego_image.png"
                save_image(stego_image, output_filename)
                
                with open(output_filename, "rb") as file:
                    btn = st.download_button(
                        label="Descargar imagen con mensaje oculto",
                        data=file,
                        file_name="imagen_oculta.png",
                        mime="image/png"
                    )
                
                st.info(f"Esta imagen fue ocultada usando {bits_hide} bits. " 
                       f"Asegúrate de recordar este número para la extracción.")
                
        except Exception as e:
            st.error(f"Error al procesar las imágenes: {str(e)}")

with tab2:
    st.header("Extraer imagen oculta")
    
    bits_extract = st.slider('Número de bits utilizados (LSB)', 1, 8, 1, key='extract_bits',
                           help='Debe coincidir EXACTAMENTE con el número usado al ocultar')
    
    output_mode = st.selectbox('Modo de color para la imagen extraída',
                              options=['RGB', 'L'],
                              format_func=lambda x: 'Color (RGB)' if x == 'RGB' else 'Escala de grises',
                              help='Selecciona el modo de color deseado para la imagen extraída')
    
    stego_file = st.file_uploader("Selecciona la imagen con mensaje oculto", type=['png'], key='stego')
    
    if stego_file:
        try:
            # Cargar imagen usando la nueva función
            stego_image = load_image(stego_file)
            stego_image = normalize_image(stego_image, 'RGB')
            
            st.image(stego_image, caption="Imagen con mensaje oculto")
            st.write(f"Dimensiones: {stego_image.shape[:2]}")
            
            if st.button("Extraer Imagen"):
                extracted_image = extract_image(stego_image, bits_extract, output_mode)
                st.image(extracted_image, caption=f"Imagen extraída usando {bits_extract} bits")
                
                # Guardar la imagen extraída
                output_filename = "extracted_image.png"
                save_image(extracted_image, output_filename)
                
                with open(output_filename, "rb") as file:
                    btn = st.download_button(
                        label="Descargar imagen extraída",
                        data=file,
                        file_name="imagen_extraida.png",
                        mime="image/png"
                    )
                
        except Exception as e:
            st.error(f"Error al procesar la imagen: {str(e)}")
