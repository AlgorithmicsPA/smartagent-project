#!/usr/bin/env python3
"""
Auditoría simple de repositorios de GitHub usando búsquedas web
"""

import requests
import time

def check_repo_for_credentials(username, repo_name):
    """Verificar un repositorio en busca de credenciales usando búsquedas web"""
    
    print(f"\n🔍 Verificando: {repo_name}")
    print(f"   🔗 URL: https://github.com/{username}/{repo_name}")
    
    # Términos críticos a buscar
    critical_terms = [
        "password",
        "token", 
        "secret",
        "api_key",
        "123",
        "admin",
        "28ZwnPHQRC",
        "npg_I6sKUNeof9qb",
        "postgresql://",
        "mysql://"
    ]
    
    found_issues = []
    
    for term in critical_terms:
        try:
            # URL de búsqueda de GitHub
            search_url = f"https://github.com/search?q=repo%3A{username}%2F{repo_name}+{term}&type=code"
            
            print(f"   🔎 Buscando: {term}")
            
            response = requests.get(search_url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            if response.status_code == 200:
                # Verificar si hay resultados
                if "No code results found" not in response.text:
                    print(f"      ⚠️  POSIBLE CREDENCIAL ENCONTRADA: {term}")
                    found_issues.append({
                        'term': term,
                        'search_url': search_url
                    })
                else:
                    print(f"      ✅ Sin resultados para: {term}")
            else:
                print(f"      ❌ Error en búsqueda: {response.status_code}")
            
            # Esperar para no sobrecargar
            time.sleep(1)
            
        except Exception as e:
            print(f"      ❌ Error: {e}")
    
    if found_issues:
        print(f"   🚨 {len(found_issues)} posibles credenciales encontradas")
        print("   📋 URLs para revisar manualmente:")
        for issue in found_issues:
            print(f"      🔗 {issue['search_url']}")
    else:
        print(f"   ✅ Sin credenciales encontradas")
    
    return found_issues

def main():
    username = "AlgorithmicsPA"
    repos = [
        'besmart',
        'n8n-samart888', 
        'Prueba'
    ]
    
    print("🚀 Auditoría de Seguridad de Repositorios GitHub")
    print("=" * 60)
    print(f"👤 Usuario: {username}")
    print(f"📊 Repositorios a auditar: {len(repos)}")
    
    all_issues = []
    
    for repo in repos:
        issues = check_repo_for_credentials(username, repo)
        if issues:
            all_issues.extend(issues)
    
    print("\n" + "=" * 60)
    print("📋 RESUMEN DE AUDITORÍA")
    print("=" * 60)
    
    if all_issues:
        print(f"🚨 SE ENCONTRARON {len(all_issues)} POSIBLES CREDENCIALES")
        print("\n🔧 ACCIONES RECOMENDADAS:")
        print("1. Revisar manualmente cada URL de búsqueda")
        print("2. Verificar si las coincidencias son credenciales reales")
        print("3. Cambiar inmediatamente cualquier credencial expuesta")
        print("4. Implementar variables de entorno")
        print("5. Configurar .gitignore para archivos sensibles")
    else:
        print("✅ ¡EXCELENTE! No se encontraron credenciales expuestas")
    
    print("\n📄 Para revisión manual completa:")
    print("1. Ve a cada repositorio en GitHub")
    print("2. Usa la función de búsqueda (Ctrl+F)")
    print("3. Busca por: password, token, secret, 123, admin")
    print("4. Revisa archivos de configuración (.env, config, etc.)")

if __name__ == "__main__":
    main() 