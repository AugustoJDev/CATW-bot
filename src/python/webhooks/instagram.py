import sys
import instaloader
import json
import re

# Inicializa o Instaloader
loader = instaloader.Instaloader()

# Função para identificar o tipo de URL
def identificar_tipo(url):
    if "/p/" in url or "/tv/" in url:  # Post ou IGTV
        return "post"
    elif "/stories/" in url:  # Stories
        return "story"
    elif "/reel/" in url:  # Reels
        return "reel"
    else:
        return "desconhecido"

# Função para extrair informações do Instagram
def obter_info_instagram(url):
    tipo = identificar_tipo(url)

    try:
        match = re.search(r'instagram\.com/([^/?]+)', url)
        if not match:
            return json.dumps({"erro": "URL inválida"})

        shortcode = match.group(1)  # Código do post/story/reel

        post = instaloader.Post.from_shortcode(loader.context, shortcode)

        dados = {
            "tipo": tipo,
            "autor": post.owner_profile,
            "descricao": post.caption,
            "imagem_autor": post.owner_profile.profile_pic_url,
            "thumbnail": post.url
        }
        
        return json.dumps(dados, ensure_ascii=False)
    
    except Exception as e:
        return json.dumps({"erro": str(e)})

if __name__ == "__main__":
    if len(sys.argv) > 1:
        url = sys.argv[1]
        resultado = obter_info_instagram(url)
        print(resultado)
    else:
        print(json.dumps({"erro": "Nenhuma URL recebida"}))
