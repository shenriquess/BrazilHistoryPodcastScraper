import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
from datetime import datetime
import os
from typing import List, Dict, Optional

class BrazilHistoryPodcastScraper:
    """
    Classe especializada em fazer web scraping dos podcasts do Leitura ObrigaHistória,
    focando especificamente em conteúdo relacionado à História do Brasil.
    """
    def __init__(self):
        """
        Inicializa o scraper com configurações básicas.
        - Define URLs base
        - Configura headers para requisições
        - Inicializa lista de palavras-chave para identificar conteúdo sobre Brasil
        """
        self.base_url = "https://leituraobrigahistoria.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        # Palavras-chave para identificar conteúdo sobre História do Brasil
        self.brazil_keywords = [
            'brasil', 'brasileiro', 'brasileira', 'império', 'dom pedro',
            'república', 'colonial', 'colônia', 'independência', 'ditadura',
            'vargas', 'military', 'indígena', 'bandeirante', 'escravo',
            'abolição', 'quilombo', 'cangaço', 'regência', 'provincial',
            'getúlio', 'jk', 'kubitschek', 'nova república', 'primeiro reinado',
            'segundo reinado', 'período regencial', 'guerra do paraguai'
        ]

    def get_soup(self, url: str) -> Optional[BeautifulSoup]:
        """
        Faz uma requisição HTTP e retorna um objeto BeautifulSoup para análise.
        Configura a codificação correta para caracteres especiais.
        
        Args:
            url (str): URL da página a ser acessada
            
        Returns:
            BeautifulSoup: Objeto para análise do HTML, ou None em caso de erro
            
        Raises:
            Trata internamente as exceções de conexão e parsing
        """
        try:
            print(f"Acessando: {url}")
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            # Força a codificação para UTF-8
            response.encoding = 'utf-8'
            return BeautifulSoup(response.text, 'html.parser', from_encoding='utf-8')
        except requests.RequestException as e:
            print(f"Erro ao acessar {url}: {e}")
            return None
        except Exception as e:
            print(f"Erro inesperado ao processar {url}: {e}")
            return None

    def discover_podcast_links(self) -> Dict[str, str]:
        """
        Descobre automaticamente os links para todos os podcasts na página principal.
        Usa uma abordagem mais genérica que procura por padrões que identificam podcasts
        em qualquer lugar da página.
        
        Returns:
            Dict[str, str]: Dicionário com nome do podcast e sua URL
        """
        podcasts = {}
        soup = self.get_soup(self.base_url)
        if not soup:
            return podcasts

        # Procura na seção principal do site
        main_content = soup.find('div', {'id': 'et-main-area'})
        if not main_content:
            print("Erro: Não foi possível encontrar a área principal do conteúdo")
            return podcasts

        # Abordagem 1: Procura por imagens com links para programas
        all_image_links = main_content.find_all('div', {'class': 'dsm-perspective-image-wrapper'})
        for wrapper in all_image_links:
            link = wrapper.find('a', href=True)
            if link and '/programa/' in link['href']:
                self._process_podcast_link(link, podcasts)

        # Abordagem 2: Procura por links diretos para programas
        all_program_links = main_content.find_all('a', href=lambda href: href and '/programa/' in href)
        for link in all_program_links:
            if not any(info['url'] == link['href'] for info in podcasts.values()):
                self._process_podcast_link(link, podcasts)

        # Abordagem 3: Procura por cards ou blocos de conteúdo
        content_blocks = main_content.find_all('div', {'class': re.compile(r'et_pb_column.*')})
        for block in content_blocks:
            link = block.find('a', href=lambda href: href and '/programa/' in href)
            if link and not any(info['url'] == link['href'] for info in podcasts.values()):
                self._process_podcast_link(link, podcasts)

        if not podcasts:
            print("Aviso: Nenhum podcast encontrado. Verifique se a estrutura do site mudou.")
        else:
            print(f"\nTotal de podcasts encontrados: {len(podcasts)}")
            for name, info in podcasts.items():
                print(f"- {info['nome']} ({info['url']})")

        return podcasts

    def _process_podcast_link(self, link_element, podcasts_dict):
        """
        Processa um elemento de link encontrado e extrai as informações do podcast.
        
        Args:
            link_element: Elemento BeautifulSoup contendo o link
            podcasts_dict: Dicionário onde as informações serão armazenadas
        """
        url = link_element['href']
        name = url.split('/')[-2]  # Extrai o nome do podcast da URL
        
        # Tenta encontrar o nome de exibição em diferentes lugares
        display_name = None
        
        # Tenta encontrar no texto do próprio link
        if link_element.text.strip():
            display_name = link_element.text.strip()
        
        # Tenta encontrar em um elemento de texto próximo
        if not display_name:
            parent = link_element.find_parent()
            if parent:
                text_div = parent.find_next_sibling('div', {'class': 'et_pb_text_inner'})
                if text_div:
                    display_name = text_div.text.strip()
        
        # Tenta encontrar em uma imagem
        if not display_name:
            img = link_element.find('img')
            if img and img.get('title'):
                display_name = img['title']
        
        # Se ainda não encontrou, usa o nome da URL formatado
        if not display_name:
            display_name = name.replace('-', ' ').title()
        
        # Adiciona ao dicionário apenas se já não existir
        if name not in podcasts_dict:
            podcasts_dict[name] = {
                'url': url,
                'nome': display_name
            }
            print(f"Novo podcast encontrado: {display_name}")

    def is_brazil_related(self, title: str) -> bool:
        """
        Verifica se um título está relacionado à História do Brasil.
        
        Args:
            title (str): Título do episódio
            
        Returns:
            bool: True se o título contiver palavras-chave relacionadas ao Brasil
        """
        title_lower = title.lower()
        return any(keyword in title_lower for keyword in self.brazil_keywords)

    def extract_episode_info(self, article_soup) -> Optional[Dict]:
        """
        Extrai informações de um episódio individual.
        
        Args:
            article_soup: Objeto BeautifulSoup contendo o HTML do artigo
            
        Returns:
            Dict: Dicionário com informações do episódio ou None se não for válido
        """
        try:
            title_elem = article_soup.find('h2', class_='dg_bm_title')
            if not title_elem or not title_elem.find('a'):
                return None

            title = title_elem.find('a').text.strip()
            if not self.is_brazil_related(title):
                return None

            link = title_elem.find('a')['href']
            date_elem = article_soup.find('span', class_='published')
            date = date_elem.text.strip() if date_elem else "Data não disponível"

            return {
                'titulo': title,
                'link': link,
                'data': date
            }
        except Exception as e:
            print(f"Erro ao extrair informações do episódio: {e}")
            return None

    def scrape_podcast_page(self, url: str) -> List[Dict]:
        """
        Extrai informações de uma página específica de podcast.
        
        Args:
            url (str): URL da página do podcast
            
        Returns:
            List[Dict]: Lista de episódios encontrados na página
        """
        episodes = []
        soup = self.get_soup(url)
        if not soup:
            return episodes

        articles = soup.find_all('article', class_='dgbm_post_item')
        for article in articles:
            episode = self.extract_episode_info(article)
            if episode:
                episodes.append(episode)

        return episodes

    def get_next_page_url(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Obtém a URL da próxima página, se existir.
        
        Args:
            soup (BeautifulSoup): Objeto BeautifulSoup da página atual
            
        Returns:
            Optional[str]: URL da próxima página ou None se não houver
        """
        next_link = soup.find('div', class_='alignleft')
        if next_link and next_link.find('a'):
            return next_link.find('a')['href']
        return None

    def scrape_podcast(self, podcast_url: str) -> List[Dict]:
        """
        Realiza o scraping completo de um podcast, incluindo todas as páginas.
        
        Args:
            podcast_url (str): URL inicial do podcast
            
        Returns:
            List[Dict]: Lista com todos os episódios relacionados ao Brasil
        """
        all_episodes = []
        current_url = podcast_url
        page_num = 1

        while current_url:
            print(f"\nProcessando página {page_num}")
            soup = self.get_soup(current_url)
            if not soup:
                break

            episodes = self.scrape_podcast_page(current_url)
            all_episodes.extend(episodes)

            current_url = self.get_next_page_url(soup)
            page_num += 1
            time.sleep(1)  # Pausa para não sobrecarregar o servidor

        return all_episodes

    def save_results(self, episodes: List[Dict], podcast_name: str):
        """
        Salva os resultados em um arquivo CSV e gera estatísticas.
        Garante a codificação correta dos caracteres especiais.
        
        Args:
            episodes (List[Dict]): Lista de episódios a serem salvos
            podcast_name (str): Nome do podcast para nomear o arquivo
        """
        if not episodes:
            print(f"Nenhum episódio sobre História do Brasil encontrado em {podcast_name}")
            return

        # Cria diretório se não existir
        os.makedirs('podcasts_brasil', exist_ok=True)
        
        # Nome do arquivo com data
        filename = f'podcasts_brasil/{podcast_name}_brasil_{datetime.now().strftime("%Y%m%d")}.csv'
        
        try:
            # Cria DataFrame
            df = pd.DataFrame(episodes)
            
            # Garante que todas as colunas de texto estejam em UTF-8
            for col in df.select_dtypes(include=['object']).columns:
                df[col] = df[col].astype(str).str.encode('utf-8').str.decode('utf-8')
            
            # Salva com configurações específicas para caracteres especiais
            df.to_csv(filename, index=False, encoding='utf-8-sig', quoting=1)
            
            print(f"\nArquivo salvo com sucesso: {filename}")
            
            # Verifica se o arquivo foi salvo corretamente
            df_check = pd.read_csv(filename, encoding='utf-8-sig')
            sample_title = df_check['titulo'].iloc[0] if not df_check.empty else "Nenhum título"
            print(f"Verificação de codificação - Primeiro título: {sample_title}")
            
            # Estatísticas
            print(f"\nEstatísticas do podcast {podcast_name}:")
            print(f"Total de episódios sobre História do Brasil: {len(episodes)}")
            print("\nPrimeiros 5 episódios encontrados:")
            for ep in episodes[:5]:
                print(f"- {ep['titulo']} ({ep['data']})")
                
        except Exception as e:
            print(f"Erro ao salvar o arquivo: {e}")
            # Tenta salvar em um formato mais simples como backup
            backup_file = f'podcasts_brasil/backup_{podcast_name}_{datetime.now().strftime("%Y%m%d")}.csv'
            df.to_csv(backup_file, index=False, encoding='utf-8-sig')

def main():
    """
    Função principal que coordena todo o processo de scraping.
    """
    print("Iniciando scraping dos podcasts do Leitura ObrigaHistória...")
    scraper = BrazilHistoryPodcastScraper()
    
    # Descobre automaticamente os podcasts
    podcasts = scraper.discover_podcast_links()
    
    if not podcasts:
        print("Nenhum podcast encontrado na página principal.")
        return
    
    print(f"\nForam encontrados {len(podcasts)} podcasts.")
    
    # Processa cada podcast
    for podcast_name, info in podcasts.items():
        print(f"\nIniciando scraping do podcast: {info['nome']}")
        episodes = scraper.scrape_podcast(info['url'])
        scraper.save_results(episodes, podcast_name)

if __name__ == "__main__":
    main()