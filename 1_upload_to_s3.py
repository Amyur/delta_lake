import os
import boto3
from pathlib import Path
from dotenv import load_dotenv
from botocore.exceptions import ClientError

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Configuración de AWS
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_DEFAULT_REGION = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
BUCKET_NAME = 'lakehouseyelp'

def upload_json_files_to_s3():
    """
    Sube todos los archivos JSON del directorio actual al bucket de S3.
    """
    # Crear cliente de S3
    s3_client = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_DEFAULT_REGION
    )
    
    # Obtener el directorio actual
    current_dir = Path(__file__).parent
    
    # Buscar todos los archivos JSON en el directorio actual
    json_files = list(current_dir.glob('*.json'))
    
    if not json_files:
        print("No se encontraron archivos JSON en el directorio actual.")
        return
    
    print(f"Se encontraron {len(json_files)} archivo(s) JSON para subir.")
    print(f"Bucket de destino: {BUCKET_NAME}\n")
    
    # Subir cada archivo JSON
    for json_file in json_files:
        try:
            file_name = json_file.name
            file_size_mb = json_file.stat().st_size / (1024 * 1024)
            
            # Definir la ruta en S3 (carpeta raw/)
            s3_key = f"raw/{file_name}"
            
            print(f"Subiendo {file_name} ({file_size_mb:.2f} MB)...")
            
            # Subir el archivo a S3
            s3_client.upload_file(
                str(json_file),
                BUCKET_NAME,
                s3_key,
                ExtraArgs={'ContentType': 'application/json'}
            )
            
            print(f"✓ {file_name} subido exitosamente a s3://{BUCKET_NAME}/{s3_key}")
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'NoSuchBucket':
                print(f"✗ Error: El bucket '{BUCKET_NAME}' no existe.")
                print(f"  Por favor, crea el bucket primero o verifica el nombre.")
            else:
                print(f"✗ Error al subir {file_name}: {e}")
        except Exception as e:
            print(f"✗ Error inesperado al subir {file_name}: {e}")
    
    print("\n¡Proceso completado!")

def verify_bucket_exists():
    """
    Verifica si el bucket existe y es accesible.
    """
    s3_client = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_DEFAULT_REGION
    )
    
    try:
        s3_client.head_bucket(Bucket=BUCKET_NAME)
        print(f"✓ El bucket '{BUCKET_NAME}' existe y es accesible.\n")
        return True
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '404':
            print(f"✗ El bucket '{BUCKET_NAME}' no existe.")
            return False
        elif error_code == '403':
            print(f"✗ No tienes permisos para acceder al bucket '{BUCKET_NAME}'.")
            return False
        else:
            print(f"✗ Error al verificar el bucket: {e}")
            return False

if __name__ == "__main__":
    print("=" * 60)
    print("SUBIDA DE ARCHIVOS JSON A S3")
    print("=" * 60)
    print()
    
    # Verificar que las credenciales estén configuradas
    if not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY:
        print("✗ Error: Las credenciales de AWS no están configuradas.")
        print("  Verifica que el archivo .env contenga AWS_ACCESS_KEY_ID y AWS_SECRET_ACCESS_KEY")
        exit(1)
    
    # Verificar que el bucket existe
    if verify_bucket_exists():
        # Subir los archivos
        upload_json_files_to_s3()
    else:
        print("\nPor favor, crea el bucket primero usando:")
        print(f"  aws s3 mb s3://{BUCKET_NAME} --region {AWS_DEFAULT_REGION}")
