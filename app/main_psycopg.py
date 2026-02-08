from fastapi import FastAPI, Response, status, HTTPException
import psycopg2
from psycopg2.extras import RealDictCursor
from pydantic import BaseModel
from typing import Optional
from random import randrange
import time
import logging

app = FastAPI(version="1.0.0.0", title="Posts API", description="A simple Posts API")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database connection with retry logic
def connect_to_database(max_retries=3, retry_delay=2):
    """Establish database connection with retry logic."""
    for attempt in range(max_retries):
        try:
            conn = psycopg2.connect(
                host='localhost', 
                database='fastapi', 
                user='postgres', 
                password='sa', 
                cursor_factory=RealDictCursor
            )
            cursor = conn.cursor()
            logger.info("Database connection was successful")
            return conn, cursor
        except Exception as error:
            logger.error(f"Database connection attempt {attempt + 1} failed: {error}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error("Max retries reached. Could not connect to database.")
                raise

# Initialize database connection
try:
    conn, cursor = connect_to_database()
except Exception as error:
    logger.critical(f"Failed to connect to database after all retries: {error}")
    # Fallback to in-memory storage for demonstration
    logger.warning("Using in-memory storage as fallback")
    conn, cursor = None, None

my_posts = [{"title": "title of post 1", "content": "content of post 1", "id": 1},
            {"title": "title of post 2", "content": "content of post 2", "id": 2}]

# Initialize database table if connection is successful
if conn and cursor:
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                id SERIAL PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                content TEXT NOT NULL,
                published BOOLEAN DEFAULT TRUE,
                rating INTEGER NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        logger.info("Posts table initialized successfully")
    except Exception as error:
        logger.error(f"Error creating posts table: {error}")
        conn.rollback()

class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None


@app.get("/")
async def get_default():
    return {"data": "Server is running"}

@app.get("/posts/")
async def get_posts():
    """Get all posts from the database or in-memory storage."""
    if conn and cursor:
        try:
            cursor.execute("SELECT * FROM posts ORDER BY id")
            posts = cursor.fetchall()
            return {"data": posts}
        except Exception as error:
            logger.error(f"Error fetching posts from database: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error fetching posts from database"
            )
    else:
        # Fallback to in-memory storage
        return {"data": my_posts}

@app.post("/posts/", status_code=status.HTTP_201_CREATED)
async def create_post(post: Post):
    #Verifico se l'oggetto post è valorizzato
    if not post:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Post data is required"
        )

    """Create a new post in the database or in-memory storage."""
    post_dict = post.model_dump()
    
    if conn and cursor:
        try:
            # Use database sequence for ID generation
            cursor.execute("INSERT INTO posts (title, content, published, rating) VALUES (%s, %s, %s, %s) RETURNING id",
                          (post_dict['title'], post_dict['content'], post_dict['published'], post_dict['rating']))
            new_id = cursor.fetchone()['id']
            conn.commit()
            
            # Return the created post with database-generated ID
            post_dict['id'] = new_id
            return {"data": post_dict}
        except Exception as error:
            conn.rollback()
            logger.error(f"Error creating post in database: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error creating post in database"
            )
    else:
        # Fallback to in-memory storage
        post_dict['id'] = randrange(0, 1000000)
        my_posts.append(post_dict)
        return {"data": post_dict}

@app.get("/posts/latest")
async def get_latest_post():
    """Get the latest post from the database or in-memory storage."""
    if conn and cursor:
        try:
            cursor.execute("SELECT * FROM posts ORDER BY id DESC LIMIT 1")
            latest_post = cursor.fetchone()
            if latest_post:
                return {"data": latest_post}
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No posts found"
                )
        except Exception as error:
            logger.error(f"Error fetching latest post from database: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error fetching latest post from database"
            )
    else:
        # Fallback to in-memory storage
        if my_posts:
            latest_post = my_posts[-1]
            return {"data": latest_post}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No posts found"
            )

@app.get("/posts/{id}")   
async def get_post(id: int): 
    """Get a specific post by ID from the database or in-memory storage."""
    if conn and cursor:
        try:
            cursor.execute("SELECT * FROM posts WHERE id = %s", (id,))
            post_dict = cursor.fetchone()
            if post_dict is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"post with id: {id} was not found"
                )
            return {"data": post_dict}
        except HTTPException:
            raise
        except Exception as error:
            logger.error(f"Error fetching post {id} from database: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error fetching post from database"
            )
    else:
        # Fallback to in-memory storage
        post_dict = next((singlepost for singlepost in my_posts if singlepost["id"] == id), None)
        if post_dict is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"post with id: {id} was not found"
            )
        return {"data": post_dict}


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(id: int):
    """Delete a post from the database or in-memory storage."""
    if conn and cursor:
        try:
            cursor.execute("DELETE FROM posts WHERE id = %s", (id,))
            if cursor.rowcount == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"post with id: {id} does not exist"
                )
            conn.commit()
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        except HTTPException:
            raise
        except Exception as error:
            conn.rollback()
            logger.error(f"Error deleting post {id} from database: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error deleting post from database"
            )
    else:
        # Fallback to in-memory storage
        index = next((i for i, p in enumerate(my_posts) if p["id"] == id), None)
        if index is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"post with id: {id} does not exist"
            )
        my_posts.pop(index)
        return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/update-post/{id}")
async def update_post(id: int, post: Post):
    """Update an existing post in the database or in-memory storage."""
    if conn and cursor:
        try:
            cursor.execute("UPDATE posts SET title = %s, content = %s, published = %s, rating = %s WHERE id = %s",
                          (post.title, post.content, post.published, post.rating, id))
            if cursor.rowcount == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"post with id: {id} does not exist"
                )
            conn.commit()
            post_dict = post.model_dump()
            post_dict['id'] = id
            return {"data": post_dict}
        except HTTPException:
            raise
        except Exception as error:
            conn.rollback()
            logger.error(f"Error updating post {id} in database: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error updating post in database"
            )
    else:
        #Verifico se trovo l'oggetto post in memoria    
        index = next((i for i, p in enumerate(my_posts) if p["id"] == id), None)
        if index is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"post with id: {id} does not exist")
        post_dict = post.model_dump()
        post_dict['id'] = id
        my_posts[index] = post_dict
        return {"data": post_dict}
