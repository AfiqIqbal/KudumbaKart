from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
import os

class KnowledgeBase:
    def __init__(self):
        self.initialized = False

    def initialize(self):
        """Initialize the knowledge base"""
        if not self.initialized:
            self.initialized = True
            return True
        return False

    def query(self, message):
        """Query the knowledge base"""
        return None

class KudumbaKartKnowledge(KnowledgeBase):
    def __init__(self):
        super().__init__()
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )
        self.text_splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        self.knowledge_base = None
        self.project_info = """
        KudumbaKart is an e-commerce platform specifically designed for Kudumbashree units in Kerala. 
        Key features include:
        
        1. Product Categories:
        - Food products (spices, snacks, etc.)
        - Handloom items
        - Handicrafts
        - Ayurvedic products
        
        2. Seller Features:
        - Easy registration for Kudumbashree units
        - Dedicated seller dashboard
        - Product management tools
        - Order tracking
        - Analytics
        
        3. Customer Features:
        - User-friendly interface
        - Secure shopping cart
        - Multiple payment options
        - Product reviews
        - Order tracking
        
        4. Delivery Information:
        - Delivery across Kerala
        - 3-5 business days delivery time
        - Cash on delivery available
        - Safe packaging
        
        5. Payment Options:
        - UPI payments
        - Card payments
        - Cash on delivery
        - Secure payment gateway
        
        6. Quality Assurance:
        - Products from verified Kudumbashree units
        - Quality checks before dispatch
        - Return policy for damaged items
        - Customer satisfaction guarantee
        
        7. Community Support:
        - Supporting local women entrepreneurs
        - Promoting traditional products
        - Economic empowerment
        - Sustainable development
        
        8. Contact Information:
        - Phone: +91 98765 43210
        - Email: info@kudumbakart.com
        - Location: Kerala, India
        """

    def initialize(self):
        """Initialize the knowledge base with project information"""
        if not super().initialize():
            return
        try:
            texts = self.text_splitter.split_text(self.project_info)
            self.knowledge_base = FAISS.from_texts(texts, self.embeddings)
            
            # Add additional information from templates
            template_dir = os.path.join(os.path.dirname(__file__), 'templates')
            for filename in os.listdir(template_dir):
                if filename.endswith('.html'):
                    with open(os.path.join(template_dir, filename), 'r', encoding='utf-8') as f:
                        content = f.read()
                        texts = self.text_splitter.split_text(content)
                        if texts:
                            temp_db = FAISS.from_texts(texts, self.embeddings)
                            self.knowledge_base.merge_from(temp_db)
            print("Knowledge base initialized successfully")
        except Exception as e:
            print(f"Error initializing knowledge base: {str(e)}")
            self.knowledge_base = None

    def query(self, question, k=3):
        """Query the knowledge base"""
        try:
            if not self.knowledge_base:
                self.initialize()
            
            docs = self.knowledge_base.similarity_search(question, k=k)
            return [doc.page_content for doc in docs]
        except Exception as e:
            print(f"Error querying knowledge base: {str(e)}")
            return []

knowledge_base = KudumbaKartKnowledge()
