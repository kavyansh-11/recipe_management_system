# Recipe Management System

This is a Django-based backend system to manage recipes. It supports role-based access for **Creators** and **Viewers**, allowing creators to upload, modify, and delete recipes, while viewers can browse, mark favourites, and download recipe PDFs.

----------

## Tech Stack

- **Backend**: Django (Python)
- **Authentication**: Email-based and Password (for role validation)
- **API**: Django REST Framework (DRF)
- **File Handling**: Excel file upload for bulk recipe creation
- **PDF Generation**: Recipes downloadable as PDF

----------

## Key Features

- Recipe creation by Creators via JSON or Excel file
- Add ingredients and instructions per recipe
- Bulk upload support using formatted Excel files
- PDF download of individual recipes
- Mark favourite recipes by viewers
- Filter recipes per creator and view details
- Basic role validation by email (Creator or Viewer)

----------

## Roles

### Creator
- Can create users
- Upload recipes with instruction and ingredients (Excel)
- View, update, or delete their own recipes

### Viewer
- Can view all recipes
- View specific detailed recipe info
- Mark recipes as favourites
- Download recipe as a PDF

----------

1. Login  

Method: POST  
Endpoint: login_view/

Form Data:
- email
- password

Response:
- Returns bearer token of authenticated user.


------------------------------------------------------------

2. Create User  

Method: POST  
Endpoint: create_user/

Form Data:
- name
- email
- password
- role

Response:
- Creates a new user successfully.


------------------------------------------------------------

3. Recipe Management  

3.1 Create Recipe  

Method: POST  
Endpoint: recipe/

Form Data:
- recipe (file)
- ingredient (file)
- instruction (file)

Response:
- Creates a new recipe along with its ingredients and instructions.


------------------------------------------------------------

3.2 Get User Created Recipes  

Method: GET  
Endpoint: recipe/

Response:
- Returns details of recipes created by the logged-in user.


------------------------------------------------------------

3.3 Modify Recipe  

Method: PUT  
Endpoint: recipe_detail/<int:recipe_id>/

Request Body (JSON):

{
  "title": "Paneer Butter Masala",
  "description": "A rich and creamy North Indian curry made with paneer.",
  "prep_duration": "15",
  "cook_duration": "30",
  "ingredients": ["Paneer", "Butter", "Tomatoes"],
  "instructions": [
    { "step_number": 1, "description": "Heat butter in a pan." },
    { "step_number": 2, "description": "Add tomato puree and cook for 5 minutes." },
    { "step_number": 3, "description": "Add paneer cubes and simmer for 10 minutes." }
  ]
}

Response:
- Updates recipe details along with ingredients and instructions.


------------------------------------------------------------

3.4 Delete Recipe  

Method: DELETE  
Endpoint: recipe_detail/<int:recipe_id>/

Response:
- Deletes the selected recipe created by the user.


------------------------------------------------------------

4. Recipe List  

Method: GET  
Endpoint: recipe_list/

Response:
- Returns the list of all available recipes.


------------------------------------------------------------

5. Recipe Detail  

Method: GET  
Endpoint: recipe_detail/<int:recipe_id>/

Response:
- Returns details of a particular recipe.


------------------------------------------------------------

6. Mark Favourite  

Method: POST  
Endpoint: mark_favourite/<int:recipe_id>/

Response:
- Marks the selected recipe as favourite for the logged-in user.


------------------------------------------------------------

Authentication:

For protected endpoints, include the bearer token in the request header:

Authorization: Bearer <your_token>
