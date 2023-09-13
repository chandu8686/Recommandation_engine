document.addEventListener('DOMContentLoaded', () => {
    const searchForm = document.getElementById('search-form');
    const searchInput = document.getElementById('search-input');
    const searchResults = document.getElementById('search-results');

    const userRecommendationForm = document.getElementById('user-recommendation-form');
    const userIdInput = document.getElementById('user-id-input');
    const userRecommendations = document.getElementById('user-recommendations');

    const userProductRecommendationForm = document.getElementById('user-product-recommendation-form');
    const userProductRecommendations = document.getElementById('user-recommended-products');


    const similarProductsForm = document.getElementById('similar-products-form');
    const skuInput = document.getElementById('sku-input');
    const similarProductsResults = document.getElementById('similar-products-results');

    const recommendedProductsForm = document.getElementById('recommended-products-form');
    const customerIdInput = document.getElementById('customer-id-input');
    const recommendedProductsResults = document.getElementById('recommended-products-results');

    const wishlistForm = document.getElementById('wishlist-form');
        const customerIdInputs = document.getElementById('customer-id-inputs');
        const wishlistResults = document.getElementById('wishlist-results');

        wishlistForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            const customer_id = customerIdInputs.value;
            fetchWishlistRecommendedProducts(customer_id);
        });

        async function fetchWishlistRecommendedProducts(customerId) {
            try {
                const response = await fetch(`/get_wishlist_products?customer_id=${encodeURIComponent(customerId)}`);
                const data = await response.json();
                displayWishlistProducts(data.recommended_products);
            } catch (error) {
                console.error('Error fetching wishlist recommended products:', error);
            }
        }

        function displayWishlistProducts(products) {
            const productsList = products.map(product => `
                <div class="col-md-4 mb-4">
                    <div class="card">
                        <img src="${product.image}" class="card-img-top" alt="${product.title}">
                        <div class="card-body">
                            <h5 class="card-title">${product.title}</h5>
                            <p class="card-text">Price: $${product.price}</p>
                            <p class="card-text">Sale Price: $${product.sale_price}</p>
                            <a href="${product.link}" class="btn btn-primary" target="_blank">Product Link</a>
                        </div>
                    </div>
                </div>
            `).join('');

            wishlistResults.innerHTML = productsList;
        }

    recommendedProductsForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        const customer_id = customerIdInput.value;

        // Fetch recommended products JSON data from your Flask API with the provided customer ID
        const response = await fetch(`/get_brought_products?customer_id=${encodeURIComponent(customer_id)}`);
        const data = await response.json();  // Parse the JSON response

        // Generate HTML content
        let htmlContent = '';
        data.recommended_products.forEach(product => {
            const sku = product.SKU;
            const product_name = product["Product Name"];
            const predicted_score = product["Predicted Score"];
            const image = product.Image;
            const link = product.Link;

            htmlContent += `
                <div class="product">
                    <h2>SKU: ${sku}</h2>
                    <h3>Product Name: ${product_name}</h3>
                    <p>Predicted Score: ${predicted_score}</p>
                    <p>Image: <img src="${image}" alt="${product_name}" width="100"></p>
                    <p>Link: <a href="${link}" target="_blank">${link}</a></p>
                </div>`;
        });

        // Display recommended products using innerHTML
        recommendedProductsResults.innerHTML = htmlContent;
    });


    similarProductsForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        const sku = skuInput.value;

        // Fetch similar products JSON data from your Flask API with the provided SKU
        const response = await fetch(`/get_similar_products?Product_ID=${encodeURIComponent(sku)}`);
        const data = await response.json();  // Parse the JSON response

        // Generate HTML content
        let htmlContent = '';
        data.similar_products.forEach(product => {
            const product_id = product.Product_ID;
            const product_name = product.Product_Name;
            const similar_products = product.Similar_Products;

            htmlContent += `
                <h2>Product ID: ${product_id}</h2>
                <h3>Product Name: ${product_name}</h3>
                <ul>`;
            
            similar_products.forEach(similar_product => {
                const similar_product_name = similar_product[0];
                const similar_product_image = similar_product[1];
                const similar_product_link = similar_product[2];

                htmlContent += `
                    <li>
                        <h4>${similar_product_name}</h4>
                        <p>Image: <img src="${similar_product_image}" alt="${similar_product_name}" width="100"></p>
                        <p>Link: <a href="${similar_product_link}" target="_blank">${similar_product_link}</a></p>
                    </li>`;
            });

            htmlContent += `
                </ul>
                <hr>`;
        });

        // Display similar products using innerHTML
        similarProductsResults.innerHTML = htmlContent;
    });




    async function fetchAndDisplaySearchResults(query) {
        // Fetch search results from your Flask API
        const response = await fetch(`/search?query=${encodeURIComponent(query)}`);
        const data = await response.json();

        // Display search results
        searchResults.innerHTML = '';
        data.forEach(product => {
            const productCard = document.createElement('div');
            productCard.className = 'card mb-3';
            productCard.innerHTML = `
                <div class="row g-0">
                    <div class="col-md-4">
                        <img src="${product.image}" alt="${product.product_name}" class="img-fluid rounded-start">
                    </div>
                    <div class="col-md-8">
                        <div class="card-body">
                            <h5 class="card-title">${product.product_name}</h5>
                            <p class="card-text">SKU: ${product.sku}</p>
                            <p class="card-text">Price: ${product.price}</p>
                            <p class="card-text">Brand: ${product.brand}</p>
                            <p class="card-text">Color: ${product.color}</p>
                            <a href="${product.link}" class="btn btn-primary btn-sm" target="_blank">Product Link</a>
                        </div>
                    </div>
                </div>
            `;
            searchResults.appendChild(productCard);
        });
    }

    async function fetchAndDisplayUserRecommendations(userId) {
        // Fetch user recommendations from your Flask API
        const response = await fetch(`/get_recommendations?user_id=${encodeURIComponent(userId)}`);
        const data = await response.json();

        // Display user recommendations
        userRecommendations.innerHTML = '';
        const recommendationList = document.createElement('ul');
        data.recommended_categories.forEach(category => {
            const listItem = document.createElement('li');
            listItem.textContent = category;
            recommendationList.appendChild(listItem);
        });
        userRecommendations.appendChild(recommendationList);
    }

    async function fetchAndDisplayUserProductRecommendations(userId) {
        // Fetch user product recommendations from your Flask API
        const response = await fetch(`/get_user_product_recommendations?user_id=${encodeURIComponent(userId)}`);
        const data = await response.json();

        // Display user product recommendations
        userProductRecommendations.innerHTML = '';
        data.recommended_products.forEach(product => {
            const productDiv = document.createElement('div');
            productDiv.className = 'recommended-product';
            productDiv.innerHTML = `
                <h3>${product.product_name}</h3>
                <p>SKU: ${product.sku}</p>
                <img src="${product.image}" alt="${product.product_name}" width="100">
                <a href="${product.link}" target="_blank">Product Link</a>
            `;
            userProductRecommendations.appendChild(productDiv);
        });
    }
    
    

    searchForm.addEventListener('submit', event => {
        event.preventDefault();
        const query = searchInput.value;
        fetchAndDisplaySearchResults(query);
    });

    userRecommendationForm.addEventListener('submit', event => {
        event.preventDefault();
        const userId = userIdInput.value;
        fetchAndDisplayUserRecommendations(userId);
    });

    userProductRecommendationForm.addEventListener('submit', event => {
        event.preventDefault();
        const userId = userIdInput.value;
        fetchAndDisplayUserProductRecommendations(userId);
    });
    fetchAndDisplaySearchResults('');
});