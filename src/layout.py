import streamlit as st
from esteganografia import ocultar_imagen,calcular_metricas, extraer_imagen
from utils import cargar_imagen, normalizar_imagen, mostrar_metricas, guardar_imagen

# Interfaz de Streamlit
st.title('Esteganografía de Imágenes')
tab1, tab2 = st.tabs(["Ocultar Imagen", "Extraer Imagen"])
with tab1:
    st.header("Ocultar una imagen")
    
    bits_ocultar = st.slider('Número de bits a utilizar (LSB)', 1, 8, 1, key='hide_bits',
                             help='Más bits = mejor calidad de la imagen oculta, pero más visible')
    
    archivo_portada = st.file_uploader("Selecciona la imagen de portada", type=['png', 'jpg', 'jpeg','jfif'], key='cover')
    archivo_secreta = st.file_uploader("Selecciona la imagen a ocultar", type=['png', 'jpg', 'jpeg', 'jfif'], key='secret')
    
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
                metricas_portada = calcular_metricas(imagen_estego,imagen_portada,imagen_secreta,bits_ocultar)
                
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
