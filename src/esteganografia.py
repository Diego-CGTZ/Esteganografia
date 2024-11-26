from skimage import img_as_float, img_as_ubyte, io
from skimage.color import rgb2gray, gray2rgb
import numpy as np
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

def calcular_metricas(original, recuperada):
    """
    Calcula métricas de error entre dos imágenes.
    """
    original = img_as_float(original)
    recuperada = img_as_float(recuperada)
    
    mse = np.mean((original - recuperada) ** 2)
    if mse == 0:
        psnr = float('inf')
    else:
        psnr = 20 * np.log10(1.0 / np.sqrt(mse))
    
    return {
        'MSE': mse,
        'PSNR': psnr
    }

def mostrar_metricas(metricas, titulo="Métricas de Calidad", bits_usados=None):
    """
    Muestra las métricas en Streamlit.
    """
    st.write(f"### {titulo}")
    
    for metrica, valor in metricas.items():
        st.write(f"{metrica}: {valor:.4f}")
    
    psnr = metricas['PSNR']
    if bits_usados is not None:
        if bits_usados >= 6:
            st.success("🟢 Calidad Excelente - Se utilizaron suficientes bits para una recuperación casi perfecta.")
        elif bits_usados >= 4:
            st.info("🟡 Buena Calidad - Se puede recuperar bastante detalle.")
        elif bits_usados >= 2:
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

def ocultar_imagen(imagen_portada, imagen_secreta, bits):
    """
    Oculta una imagen en otra usando LSB.
    """
    # Asegurar que las imágenes sean de 8 bits
    portada = img_as_ubyte(imagen_portada.copy())
    secreta = img_as_ubyte(imagen_secreta.copy())
    
    # Crea la máscara para los bits menos significativos elegidos
    mascara_portada = 256 - (2**bits)
    # Crea la máscara para los bits más significativos
    mascara_secreta = 2**bits - 1
    
    # Limpiar los LSB de la imagen de portada
    portada_limpia = portada & mascara_portada
    
    # Preparar los bits de la imagen secreta
    bits_secreta = (secreta >> (8 - bits)) & mascara_secreta
    
    # Combinar las imágenes
    estego = portada_limpia | bits_secreta
    
    return estego

def extraer_imagen(imagen_estego, bits, modo_salida='RGB'):
    """
    Extrae la imagen oculta.
    """
    # Asegurar que la imagen esté en uint8
    estego = img_as_ubyte(imagen_estego.copy())
    
    # Crear máscara para extraer los LSB
    mascara = 2**bits - 1
    
    # Extraer los bits ocultos
    extraida = (estego & mascara)
    
    # Escalar los valores extraídos al rango completo
    extraida = (extraida << (8 - bits))
    
    # Convertir al modo de color deseado si es necesario
    if modo_salida == 'L' and len(extraida.shape) == 3:
        extraida = rgb2gray(extraida)
    elif modo_salida == 'RGB' and len(extraida.shape) == 2:
        extraida = gray2rgb(extraida)
    
    return extraida

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

# Interfaz de Streamlit
st.title('Esteganografía de Imágenes')

tab1, tab2 = st.tabs(["Ocultar Imagen", "Extraer Imagen"])

with tab1:
    st.header("Ocultar una imagen")
    
    bits_ocultar = st.slider('Número de bits a utilizar (LSB)', 1, 8, 1, key='hide_bits',
                             help='Más bits = mejor calidad de la imagen oculta, pero más visible')
    
    archivo_portada = st.file_uploader("Selecciona la imagen de portada", type=['png', 'jpg', 'jpeg'], key='cover')
    archivo_secreta = st.file_uploader("Selecciona la imagen a ocultar", type=['png', 'jpg', 'jpeg'], key='secret')
    
    if archivo_portada and archivo_secreta:
        try:
            # Cargar imágenes usando la nueva función
            imagen_portada = cargar_imagen(archivo_portada)
            imagen_secreta = cargar_imagen(archivo_secreta)
            
            # Asegurar que las imágenes estén en RGB
            imagen_portada = normalizar_imagen(imagen_portada, 'RGB')
            imagen_secreta = normalizar_imagen(imagen_secreta, 'RGB')
            
            # Ajustar tamaños
            altura_minima = min(imagen_portada.shape[0], imagen_secreta.shape[0])
            anchura_minima = min(imagen_portada.shape[1], imagen_secreta.shape[1])
            imagen_portada = imagen_portada[:altura_minima, :anchura_minima]
            imagen_secreta = imagen_secreta[:altura_minima, :anchura_minima]
            
            col1, col2 = st.columns(2)
            with col1:
                st.image(imagen_portada, caption="Imagen de portada")
                st.write(f"Dimensiones: {imagen_portada.shape[:2]}")
            with col2:
                st.image(imagen_secreta, caption="Imagen a ocultar")
                st.write(f"Dimensiones: {imagen_secreta.shape[:2]}")
            
            if st.button("Ocultar Imagen"):
                imagen_estego = ocultar_imagen(imagen_portada, imagen_secreta, bits_ocultar)
                metricas_portada = calcular_metricas(imagen_portada, imagen_estego)
                
                st.image(imagen_estego, caption="Imagen con mensaje oculto")
                mostrar_metricas(metricas_portada, "Métricas de calidad - Imagen de portada", bits_ocultar)
                
                # Guardar la imagen en formato PNG
                nombre_archivo_salida = "imagen_estego.png"
                guardar_imagen(imagen_estego, nombre_archivo_salida)
                
                with open(nombre_archivo_salida, "rb") as archivo:
                    btn = st.download_button(
                        label="Descargar imagen con mensaje oculto",
                        data=archivo,
                        file_name="imagen_oculta.png",
                        mime="image/png"
                    )
                
                st.info(f"Esta imagen fue ocultada usando {bits_ocultar} bits. " 
                       f"Asegúrate de recordar este número para la extracción.")
                
        except Exception as e:
            st.error(f"Error al procesar las imágenes: {str(e)}")

with tab2:
    st.header("Extraer imagen oculta")
    
    bits_extraer = st.slider('Número de bits utilizados (LSB)', 1, 8, 1, key='extract_bits',
                             help='Debe coincidir EXACTAMENTE con el número usado al ocultar')
    
    modo_salida = st.selectbox('Modo de color para la imagen extraída',
                               options=['RGB', 'L'],
                               format_func=lambda x: 'Color (RGB)' if x == 'RGB' else 'Escala de grises',
                               help='Selecciona el modo de color deseado para la imagen extraída')
    
    archivo_estego = st.file_uploader("Selecciona la imagen con mensaje oculto", type=['png'], key='stego')
    
    if archivo_estego:
        try:
            # Cargar imagen usando la nueva función
            imagen_estego = cargar_imagen(archivo_estego)
            imagen_estego = normalizar_imagen(imagen_estego, 'RGB')
            
            st.image(imagen_estego, caption="Imagen con mensaje oculto")
            st.write(f"Dimensiones: {imagen_estego.shape[:2]}")
            
            if st.button("Extraer Imagen"):
                imagen_extraida = extraer_imagen(imagen_estego, bits_extraer, modo_salida)
                st.image(imagen_extraida, caption=f"Imagen extraída usando {bits_extraer} bits")
                
                # Guardar la imagen extraída
                nombre_archivo_salida = "imagen_extraida.png"
                guardar_imagen(imagen_extraida, nombre_archivo_salida)
                
                with open(nombre_archivo_salida, "rb") as archivo:
                    btn = st.download_button(
                        label="Descargar imagen extraída",
                        data=archivo,
                        file_name="imagen_extraida.png",
                        mime="image/png"
                    )
                
        except Exception as e:
            st.error(f"Error al procesar la imagen: {str(e)}")
