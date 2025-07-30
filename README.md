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

`/create_user/` | `POST` | Create a new user (creator or viewer) |
`/upload_recipe_data/` | `POST` | Upload multiple recipes via Excel |
`/view_recipe_data/` | `GET` | View all recipes created by a specific user |
`/delete_recipe/<recipe_id>/<email>/` | `DELETE` | Delete a specific recipe |
`/modify_recipe/<recipe_id>/<email>/` | `PUT` | Modify specific existing recipe |

`/all_recipe/` | `GET` | List all available recipes |
`/recipe_detail/?recipe_id=ID/` | `GET` | Get detailed view of a recipe |
`/mark_favourite/` | `POST` | Mark or unmark a recipe as favourite |
`/recipes/<recipe_id>/pdf/` | `GET` | Download recipe as a PDF |

---

## Sample Modify Recipe Payload

```json
{
  "title": "Paneer Butter Masala",
  "description": "A rich and creamy North Indian curry made with paneer.",
  "prep_duration": "15",
  "cooking_time": "30",
  "ingredients": [
    { "name": "Paneer" },
    { "name": "Butter" },
    { "name": "Tomatoes" }
  ],
  "instructions": [
    { "step_number": 1, "description": "Heat butter in a pan." },
    { "step_number": 2, "description": "Add tomato puree and cook for 5 minutes." },
    { "step_number": 3, "description": "Add paneer cubes and simmer for 10 minutes." }
  ]
}
