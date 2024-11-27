from skimage import img_as_ubyte, io
from skimage.color import rgb2gray, gray2rgb
import numpy as np

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
    # Asegurar que la imagen esté en 8bits 
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

def calcular_metricas(imagen_estego, imagen_portada, imagen_secreta, bits_ocultar):
    """
    Calcula métricas comparando la imagen original, la imagen de portada y la imagen extraída.
    
    Parámetros:
    - imagen_estego: Imagen con mensaje oculto
    - imagen_portada: Imagen de portada original
    - imagen_secreta: Imagen secreta original
    - bits_ocultar: Número de bits usados para ocultar
    
    Retorna:
    Diccionario con métricas de la imagen de portada y la imagen secreta
    """
    # Extraer la imagen oculta
    imagen_extraida = extraer_imagen(imagen_estego, bits_ocultar, modo_salida='RGB')
    
    max_pixel = 255.0    
    # Métricas para la imagen secreta
    mse_secreta = np.mean((imagen_secreta - imagen_extraida) ** 2)
    psnr_secreta = 10 * np.log10((max_pixel ** 2) / mse_secreta)
    
    return {
        'MSE': mse_secreta,
        'PSNR': psnr_secreta
    }