#!/usr/bin/env python3
"""
Import collected local data into EVY RAG service
"""

import asyncio
import json
import os
import sys
import requests
import logging
from typing import List, Dict
from datetime import datetime

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGImporter:
    """Imports local data into the RAG service"""
    
    def __init__(self, rag_service_url: str = "http://localhost:8003"):
        self.rag_service_url = rag_service_url
        self.session = requests.Session()
    
    async def check_rag_service(self) -> bool:
        """Check if RAG service is available"""
        try:
            response = self.session.get(f"{self.rag_service_url}/health")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"RAG service not available: {e}")
            return False
    
    async def import_document(self, document: Dict) -> bool:
        """Import a single document to the RAG service"""
        try:
            payload = {
                "text": document["text"],
                "metadata": document.get("metadata", {})
            }
            
            # Add title if available
            if "title" in document:
                payload["metadata"]["title"] = document["title"]
            
            # Add category if available
            if "category" in document:
                payload["metadata"]["category"] = document["category"]
            
            response = self.session.post(
                f"{self.rag_service_url}/add",
                json=payload
            )
            
            if response.status_code == 200:
                logger.info(f"Imported: {document.get('title', 'Untitled')}")
                return True
            else:
                logger.error(f"Failed to import {document.get('title', 'Untitled')}: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error importing document: {e}")
            return False
    
    async def import_bulk_documents(self, documents: List[Dict]) -> Dict:
        """Import multiple documents to the RAG service"""
        if not await self.check_rag_service():
            logger.error("RAG service is not available")
            return {"success": 0, "failed": len(documents), "errors": ["RAG service unavailable"]}
        
        success_count = 0
        failed_count = 0
        errors = []
        
        logger.info(f"Starting bulk import of {len(documents)} documents")
        
        for i, document in enumerate(documents):
            try:
                if await self.import_document(document):
                    success_count += 1
                else:
                    failed_count += 1
                    errors.append(f"Failed to import document {i+1}")
                
                # Progress indicator
                if (i + 1) % 10 == 0:
                    logger.info(f"Processed {i+1}/{len(documents)} documents")
                    
            except Exception as e:
                failed_count += 1
                errors.append(f"Error importing document {i+1}: {str(e)}")
        
        logger.info(f"Import completed: {success_count} success, {failed_count} failed")
        return {
            "success": success_count,
            "failed": failed_count,
            "errors": errors
        }
    
    async def import_from_file(self, filepath: str) -> Dict:
        """Import documents from a JSON file"""
        try:
            with open(filepath, 'r') as f:
                documents = json.load(f)
            
            if not isinstance(documents, list):
                logger.error("JSON file must contain a list of documents")
                return {"success": 0, "failed": 0, "errors": ["Invalid JSON format"]}
            
            return await self.import_bulk_documents(documents)
            
        except FileNotFoundError:
            logger.error(f"File not found: {filepath}")
            return {"success": 0, "failed": 0, "errors": [f"File not found: {filepath}"]}
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in file: {e}")
            return {"success": 0, "failed": 0, "errors": [f"Invalid JSON: {str(e)}"]}
        except Exception as e:
            logger.error(f"Error reading file: {e}")
            return {"success": 0, "failed": 0, "errors": [f"File read error: {str(e)}"]}
    
    async def test_rag_service(self) -> Dict:
        """Test the RAG service with a sample query"""
        try:
            test_query = {
                "query": "weather",
                "top_k": 3
            }
            
            response = self.session.post(
                f"{self.rag_service_url}/search",
                json=test_query
            )
            
            if response.status_code == 200:
                results = response.json()
                return {
                    "status": "working",
                    "results_count": len(results.get("documents", [])),
                    "sample_results": results.get("documents", [])[:2]
                }
            else:
                return {
                    "status": "error",
                    "error": f"HTTP {response.status_code}",
                    "details": response.text
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

async def main():
    """Main import function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Import local data into EVY RAG service")
    parser.add_argument("--file", "-f", help="JSON file to import")
    parser.add_argument("--url", "-u", default="http://localhost:8003", help="RAG service URL")
    parser.add_argument("--test", "-t", action="store_true", help="Test RAG service")
    parser.add_argument("--latest", "-l", action="store_true", help="Import latest collected data")
    
    args = parser.parse_args()
    
    importer = RAGImporter(args.url)
    
    if args.test:
        print("🧪 Testing RAG service...")
        test_result = await importer.test_rag_service()
        print(f"Status: {test_result['status']}")
        if test_result['status'] == 'working':
            print(f"✅ RAG service is working! Found {test_result['results_count']} results for 'weather'")
            if test_result.get('sample_results'):
                print("Sample results:")
                for result in test_result['sample_results']:
                    print(f"  - {result[:100]}...")
        else:
            print(f"❌ RAG service error: {test_result.get('error', 'Unknown error')}")
        return
    
    if args.latest:
        # Find the latest collected data file
        collected_dir = "data/collected"
        if not os.path.exists(collected_dir):
            print(f"❌ No collected data directory found at {collected_dir}")
            print("Run collect_local_data.py first to gather local data")
            return
        
        files = [f for f in os.listdir(collected_dir) if f.endswith('.json')]
        if not files:
            print(f"❌ No collected data files found in {collected_dir}")
            print("Run collect_local_data.py first to gather local data")
            return
        
        # Get the most recent file
        latest_file = max(files, key=lambda f: os.path.getctime(os.path.join(collected_dir, f)))
        filepath = os.path.join(collected_dir, latest_file)
        print(f"📁 Using latest data file: {filepath}")
    elif args.file:
        filepath = args.file
    else:
        print("❌ Please specify either --file, --latest, or --test")
        return
    
    print(f"📥 Importing data from {filepath} to RAG service at {args.url}")
    
    # Check if RAG service is available
    if not await importer.check_rag_service():
        print(f"❌ RAG service is not available at {args.url}")
        print("Make sure the RAG service is running:")
        print("  docker-compose -f docker-compose.lilevy.yml up -d local-rag")
        return
    
    # Import the data
    result = await importer.import_from_file(filepath)
    
    print(f"\n📊 Import Results:")
    print(f"  ✅ Successfully imported: {result['success']} documents")
    print(f"  ❌ Failed to import: {result['failed']} documents")
    
    if result['errors']:
        print(f"  ⚠️  Errors:")
        for error in result['errors'][:5]:  # Show first 5 errors
            print(f"    - {error}")
        if len(result['errors']) > 5:
            print(f"    ... and {len(result['errors']) - 5} more errors")
    
    if result['success'] > 0:
        print(f"\n🎉 Successfully imported {result['success']} documents to RAG service!")
        print(f"🔍 Test the import by searching at: {args.url}/docs")

if __name__ == "__main__":
    asyncio.run(main())
