![imagen](https://github.com/AlejandroAl/Xoloitzucha/blob/main/xoloitzcucha-logo.jpg)


# Xoloitzucha


#Instrucciones de uso 

Descargar los recursos para inicar el agente para subir audios:

https://recursos-xoloitzcucha.s3.us-east-2.amazonaws.com/AgenteXoloitzSube.zip

1. Ingresar a la carpeta donde se encuentra nuestro ejecutable desde una terminal

2. Agregar los permisos de ejcución: 

   * click derecho sobre el agente ejecutable
   * navegar en la pestaña de permisos
   * Seleccionar la opción "Permitir que estee archivo se ejecute como programa", esta frase puede variar entre SO.

3. Ejecutar el siguiente comando sustituyendo el valor path, por el nombre completo de la carpeta donde subieremos nuestros archivos .wav

./XoloitzSube  testing-audio-upload path us-east-2

EJEMPLO:

./XoloitzSube  testing-audio-upload /home/alejandro/Descargas/AgenteXoloitzSube/audios/ us-east-2

como se puede observar debe contener el / inicial y final

4. Agregar uno a uno las grabaciones que se desean clasificar.

5. Ingresar al dashboard en tiempo real.

https://search-elastic-xoloitzcucha-5v7rj5hvpmn3mffggwmswemgry.us-east-2.es.amazonaws.com/_plugin/kibana/goto/05a42e91871a1107ae629b9d9169ab89?security_tenant=private


# Diagrama de arquitectura
![imagen](https://github.com/AlejandroAl/Xoloitzucha/blob/main/DiagramaArquitecturaXoloitzcucha.jpg)
