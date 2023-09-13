from flask import Flask, request, jsonify,render_template
from elasticsearch import Elasticsearch
import os

app = Flask(__name__)

# Connect to Elasticsearch
es_host = os.environ['ELASTICSEARCH_HOSTS']
print('Elastic host is {}'.format(es_host))
es = Elasticsearch([es_host])
@app.route('/')
def index():
    return render_template('./B_index.html')

@app.route('/get_recommendations', methods=['GET'])
def get_recommendations():
    user_id = request.args.get('user_id', '')
    recommendations = fetch_recommendations(user_id)  # Implement your function to fetch recommendations
    return jsonify({"recommended_categories": recommendations})

def fetch_recommendations(user_id):
    # Fetch user recommendations from the Elasticsearch index
    search_body = {
        "query": {
            "match": {
                "customer_id": user_id
            }
        }
    }
    results = es.search(index='user_category_recommendations', body=search_body)
    
    if results["hits"]["total"]["value"] == 0:
        return []  # No recommendations found for the user

    recommended_categories = results["hits"]["hits"][0]["_source"]["recommended_categories"]
    return recommended_categories

def fetch_product_recommendations(user_id):
    # Fetch user product recommendations from the Elasticsearch index
    search_body = {
        "query": {
            "match": {
                "customer_id": user_id
            }
        }
    }
    results = es.search(index='user_product_recommendations', body=search_body)
    
    if results["hits"]["total"]["value"] == 0:
        return []  # No product recommendations found for the user

    recommended_products = results["hits"]["hits"][0]["_source"]["recommended_products"]
    return recommended_products

@app.route('/get_user_product_recommendations', methods=['GET'])
def get_user_product_recommendations():
    user_id = request.args.get('user_id', '')

    product_recommendations = fetch_product_recommendations(user_id)
    return jsonify({"recommended_products": product_recommendations})


# Define the API route
@app.route('/search', methods=['GET'])
def search_api():
    user_query = request.args.get('query', '')
    search_results=''
    if user_query !='':
        search_results = perform_search(user_query)


    response = []
    for result in search_results:
        product_info = {
            "product_name": result["_source"]["product_name"],
            "sku": result["_source"]["sku"],
            "color": result["_source"]["color"],
            "size": result["_source"]["size"],
            "brand": result["_source"]["brand"],
            "price": result["_source"]["price"],
            "image": result["_source"]["image link"],
            "link": result["_source"]["link"]
        }
        response.append(product_info)

    return jsonify(response)

def perform_search(query):
    # search_body = {
    #     "query": {
    #         "multi_match": {
    #             "query": query,
    #             "fields": ["product_name","brand","color","size","description"]
    #         }
    #     }
    # }
    # search_body = {
    # "query": {
    #     "bool": {
    #         "should": [
    #             {
    #                 "multi_match": {
    #                     "query": query,
    #                     "fields": ["product_name","category", "brand", "color", "size", "description"],
    #                     "fuzziness": "AUTO"
    #                 }
    #             },
    #             {
    #                 "match": {
    #                     "keywords": {
    #                         "query": query,
    #                         "fuzziness": "AUTO"
    #                     }
    #                 }
    #             }
    #             # You can add more fuzzy matching or filters as needed
    #         ],
    #         "minimum_should_match": 1
    #             }
    #         }
    #     }

#     search_body = {
#     "query": {
#         "bool": {
#             "should": [
#                 {
#                     "match": {
#                         "product_name": {
#                             "query": query,
#                             "boost": 5  # Boosting exact matches
#                         }
#                     }
#                 },
#                 {
#                     "multi_match": {
#                         "query": query,
#                         "fields": ["product_name", "category", "brand", "color", "size", "description"],
#                         "fuzziness": "AUTO"
#                     }
#                 }
#                 # You can add more fuzzy matching or filters as needed
#             ],
#             "minimum_should_match": 1
#         }
#     }
# } 
    search_body = {
    "query": {
        "bool": {
            "should": [
                {
                    "match": {
                        "product_name": {
                            "query": query,
                            "boost": 2  # Boosting exact matches
                        }
                    }
                },
                {
                    "multi_match": {
                        "query": query,
                        "fields": ["product_name", "category", "brand", "color", "size", "description"],
                        "fuzziness": "AUTO"
                    }
                },
                {
                    "match": {
                        "entities": {
                            "query": query,
                            "fuzziness": "AUTO"
                        }
                    }
                },
                # You can add more fuzzy matching or filters as needed
            ],
            "minimum_should_match": 1
        }
    }
    }


    results = es.search(index='search_index', body=search_body,size=100)
    return results["hits"]["hits"]

@app.route('/get_similar_products', methods=['GET'])
def get_similar_products():
    sku = request.args.get('Product_ID', '')  # Get SKU from query parameters

    # Construct Elasticsearch query
    query = {
        "query": {
            "term": {
                "Product_ID": sku  # Update this field name based on your Elasticsearch index
            }
        }
    }

    # Perform the Elasticsearch search
    results = es.search(index='similar_products', body=query)


    # Process results and return as JSON response
    similar_products = []
    for hit in results['hits']['hits']:
        source = hit["_source"]
        product_id = source["Product_ID"]
        product_name = source["Product_Name"]
        extracted_similar_products = source["Extracted_Similar_Products"]
        
        similar_product_list = []
        for similar_product in extracted_similar_products:
            similar_product_name = similar_product[0]
            similar_product_image = similar_product[1]
            similar_product_link = similar_product[2]
            
            similar_product_list.append([similar_product_name, similar_product_image, similar_product_link])
        
        similar_products.append({
            "Product_ID": product_id,
            "Product_Name": product_name,
            "Similar_Products": similar_product_list
        })

    return jsonify({"similar_products": similar_products})

@app.route('/get_brought_products')
def get_recommended_products():
    customer_id = request.args.get('customer_id', '')

    query = {
        "query": {
            "match": {
                "Customer ID": customer_id
            }
        }
    }

    result = es.search(index='brought_products', body=query)

    hits = result["hits"]["hits"]
    recommended_products = []
    for hit in hits:
        customer_id = hit["_source"]["Customer ID"]
        recommended_products.extend(hit["_source"]["Recommended Products"])

    return jsonify({"recommended_products": recommended_products})

@app.route('/get_trending_brands', methods=['GET'])
def get_trending_brands():
    # Retrieve trending brands from Elasticsearch
    query = {
        'size': 100,  # Adjust the size as needed
        'query': {
            'match_all': {}
        }
    }
    results = es.search(index='trending_brands', body=query)

    # Process and format the search results
    trending_brands = [hit['_source']['brand'] for hit in results['hits']['hits']]

    return jsonify({'trending_brands': trending_brands})

@app.route('/get_popular_brands', methods=['GET'])
def get_popular_brands():
    # Retrieve popular brands from Elasticsearch
    query = {
        'size': 100,  # Adjust the size as needed
        'query': {
            'match_all': {}
        }
    }
    results = es.search(index='popular_brands', body=query)

    # Process and format the search results
    popular_brands = [hit['_source']['brand'] for hit in results['hits']['hits']]

    return jsonify({'popular_brands': popular_brands})

@app.route('/get_trending_products', methods=['GET'])
def get_trending_products():
    # Retrieve trending product details from Elasticsearch
    query = {
        'size': 100,  # Adjust the size as needed
        'query': {
            'match_all': {}
        }
    }
    results = es.search(index='trending_products', body=query)

    # Process and format the search results
    trending_products = []
    for hit in results['hits']['hits']:
        product = hit['_source']
        trending_products.append({
            'title': product['title'],
            'price': product['price'],
            'sale_price': product['sale_price'],
            'brand': product['brand'],
            'color': product['color'],
            'category': product['category'],
            'subcategory': product['subcategory'],
            'maincategory': product['maincategory'],
            'image_link': product['image_link'],
            'link': product['link']
        })

    return jsonify({'trending_products': trending_products})

@app.route('/get_wishlist_products', methods=['GET'])
def get_wishlist_recommended_products():
    # Get the customer_id parameter from the request
    customer_id = request.args.get('customer_id', '')

    # Define the search query
    query = {
        'query': {
            'match': {
                'customer_id': customer_id
            }
        }
    }

    # Perform the search
    result = es.search(index='wishlist_recommended_products', body=query)

    # Process and format the search results
    recommended_products = []
    hits = result['hits']['hits']
    for hit in hits:
        customer_id = hit['_source']['customer_id']
        products = hit['_source']['recommended_products']

        for product in products:
            sku = product['SKU']
            title = product['title']
            image = product['image']
            price = product['price']
            sale_price = product['sale_price']
            link = product['link']

            recommended_products.append({
                'customer_id': customer_id,
                'SKU': sku,
                'title': title,
                'image': image,
                'price': price,
                'sale_price': sale_price,
                'link': link
            })

    return jsonify({'recommended_products': recommended_products})



if __name__ == '__main__':
    app.run(debug=True)
