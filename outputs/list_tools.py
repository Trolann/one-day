list_tools = [
   {
       "name": "shopping",
       "description": "Only items to be purchased. Does not include chores like finding recipes or doing the shopping."
                      "Should only be individual items for a shopping list, "
                      "nothing generic like `ingredients for pasta`, `things for soup`, etc. Those should be added as"
                      "chores such as `add pasta ingredients to shopping list` or `find ingredients for soup`.",
       "input_schema": {
           "type": "object",
           "properties": {
               "title": {
                   "type": "string",
                   "description": "The name of the item to shop for."
               },
               "description": {
                   "type": "string",
                   "description": "Details about the shopping task which may include quantity, size, etc."
               },
               "due_date": {
                   "type": "string",
                   "description": "When it must be purchased by."
               },
               "labels": {
                   "type": "array",
                   "items": {
                       "type": "string",
                       "enum": [
                           "amazon",
                           "costco",
                           "groceries",
                           "target"
                       ]
                   },
                   "description": "Where the item should be purchased from. If unknown, omit"
               }
           },
           "required": ["title"]
       }
   },
   {
       "name": "chores",
       "description": "A list of chores, errands to be completed. "
                      "Includes going to the store to buy things from the shopping list, cleaning, admin tasks, etc. "
                      "Does not include school work.",
       "input_schema": {
           "type": "object",
           "properties": {
               "title": {
                   "type": "string",
                   "description": "The chore/errand/task to be completed. Be concise."
               },
               "description": {
                   "type": "string",
                   "description": "Details about the chore, where it needs to be done, etc."
               },
               "due_date": {
                   "type": "string",
                   "description": "When the chore needs to be completed"
               }
           },
           "required": ["title"]
       }
   },
   {
       "name": "meals",
       "description": "Meals available for the week. Assume groceries are in the house."
                      "Items in this list answer the question 'What's for dinner?' and won't include tasks like "
                      "going to the store to buy ingredients or individual items like 'chicken' or 'milk'.",
       "input_schema": {
           "type": "object",
           "properties": {
               "title": {
                   "type": "string",
                   "description": "The name of the meal. Example: Spaghetti, Tacos, etc."
               },
               "description": {
                   "type": "string",
                   "description": "Any details about the meal."
               }
           },
           "required": ["title"]
       }
   },
   {
       "name": "unknown",
       "description": "Anything which seems like an item but the category/list can't be determined. "
                      "This is the catch all",
       "input_schema": {
           "type": "object",
           "properties": {
               "title": {
                   "type": "string",
                   "description": "The title of the task"
               },
               "description": {
                   "type": "string",
                   "description": "Details about the task"
               },
               "due_date": {
                   "type": "string",
                   "description": "When the task needs to be completed"
               }
           },
           "required": ["title"]
       }
   },
   {
       "name": "school_work",
       "description": "A list of homework, projects, exams and other related school work to complete.",
       "input_schema": {
           "type": "object",
           "properties": {
               "title": {
                   "type": "string",
                   "description": "The class name and title of the assignment."
                                  "Format: CLASS123: Assignment Name. Example: CS166: HW1. "
                                  "Current classes enrolled: "
                                  "CMPE148	Computer Networks 1"
                                  "CS151	Object Oriented Design"
                                  "CS166	Information Security"
                                  "CMPE172	Enterprise Software Platforms"
               },
               "description": {
                   "type": "string",
                   "description": "Details about the school work such as problem numbers, notes, "
                                  "or any other details about completing it"
               },
               "due_date": {
                   "type": "string",
                   "description": "When the assignment is due, or the exam will take place."
               },
               "labels": {
                   "type": "array",
                   "items": {
                       "type": "string",
                       "enum": [
                           "administrative",
                           "homework",
                           "project"
                       ]
                   },
                   "description": "Categories related to the school work task. If unknown, use homework"
               }
           },
           "required": ["title", "labels"]
       }
   }
]