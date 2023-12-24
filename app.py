import streamlit as st
import pandas as pd
import mysql.connector
import base64

# Function to establish a connection to the SQLite database
def create_connection():
    db_config = {
        "host": "localhost",
        "user": "root",
        "password": <your-password>,
        "database": "fashionify"
    }
    conn = mysql.connector.connect(**db_config)
    return conn
def get_session_state():
    return st.session_state
# Function to create a table
def create_table(conn, query):
    try:
        c = conn.cursor()
        c.execute(query)
        conn.commit()
        st.success("Table created successfully")
    except Exception as e:
        st.error(f"Error: {e}")

# Function to execute a query
def execute_query(conn, query, data=None):
    try:
        c = conn.cursor()
        if data:
            c.execute(query, data)
        else:
            c.execute(query)
        c.fetchall()
        conn.commit()
        st.success("Query executed successfully")
    except Exception as e:
        st.error(f"Error: {e}")

def add_to_cart_and_update_quantity(connection, user_id, product_id, quantity):
    try:
        cursor = connection.cursor()
        cursor.callproc("add_to_cart_and_update_quantity", (user_id, product_id, quantity))
        connection.commit()
        st.success("Item added to the cart and product quantity updated successfully")
    except Exception as e:
        st.error(f"The error '{e}' occurred")



# Function to perform CRUD operations on the User table
def user_crud():
    st.header("User CRUD Operations")

    # Get or create session state
    session_state = st.session_state

    # Create User Table
    create_user_table_query = """
    CREATE TABLE IF NOT EXISTS User (
        UserID INTEGER PRIMARY KEY AUTO_INCREMENT,
        Username TEXT NOT NULL,
        Password TEXT NOT NULL,
        Email TEXT NOT NULL,
        Role TEXT NOT NULL
    );
    """
    create_table(create_connection(), create_user_table_query)

    # Select operation
    operation = st.selectbox("Select Operation", ["Insert", "Display", "Update", "Delete"])

    if operation == "Insert":
        # Insert User
        username = st.text_input("Username", key="insert_username")
        password = st.text_input("Password", type="password", key="insert_password")
        email = st.text_input("Email", key="insert_email")
        role = st.selectbox("Role", ["admin", "customer"], key="insert_role")

        if st.button("Insert User"):
            # Insert with an auto-incremented UserID
            insert_user_query = "INSERT INTO User (Username, Password, Email, Role) VALUES (%s, %s, %s, %s);"
            execute_query(create_connection(), insert_user_query, (username, password, email, role,))

    elif operation == "Display":
        # Display Users
        if st.button("Display Users"):
            display_users_query = "SELECT * FROM User;"
            users = pd.read_sql_query(display_users_query, create_connection())
            st.dataframe(users)

    elif operation == "Update":
        # Update User
        user_id = st.number_input("Enter User ID to Update", min_value=1, key="update_id")
        new_username = st.text_input("New Username", key="update_username")
        new_password = st.text_input("New Password", type="password", key="update_password")
        new_email = st.text_input("New Email", key="update_email")
        new_role = st.selectbox("New Role", ["admin", "customer"], key="update_role")

        if st.button("Update User"):
            update_user_query = "UPDATE User SET Username=%s, Password=%s, Email=%s, Role=%s WHERE UserID=%s;"
            execute_query(create_connection(), update_user_query, (new_username, new_password, new_email, new_role, user_id))

    elif operation == "Delete":
        # Delete User
        user_id = st.number_input("Enter User ID to Delete", min_value=1, key="delete_id")

        if st.button("Delete User"):
            delete_user_query = "DELETE FROM User WHERE UserID=%s;"
            execute_query(create_connection(), delete_user_query, (user_id,))


# Function to perform CRUD operations on the Cart table
def cart_crud():
    st.header("Cart CRUD Operations")

    # Get or create session state
    session_state = st.session_state

    # Create Cart Table
    create_cart_table_query = """
    CREATE TABLE IF NOT EXISTS Cart (
        CartID INTEGER PRIMARY KEY AUTO_INCREMENT,
        UserID INTEGER,
        ProductID INTEGER,
        Quantity INTEGER,
        Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (UserID) REFERENCES User(UserID),
        FOREIGN KEY (ProductID) REFERENCES Product(ProductID)
    );
    """
    create_table(create_connection(), create_cart_table_query)

    # Select operation
    operation = st.selectbox("Select Operation", ["Insert", "Display", "Update", "Delete"])
    create_procedure_query = """
    CREATE PROCEDURE IF NOT EXISTS add_to_cart_and_update_quantity(
        in_user_id INT,
        in_product_id INT,
        in_quantity INT
    )
    BEGIN
        DECLARE current_product_quantity INT;

        -- Insert the item into the Cart table
        INSERT INTO Cart (UserID, ProductID, Quantity)
        VALUES (in_user_id, in_product_id, in_quantity);

        -- Get the current quantity of the product
        SELECT StockQuantity INTO current_product_quantity
        FROM Product
        WHERE ProductID = in_product_id;

        -- Update the product quantity by decrementing it
        UPDATE Product
        SET StockQuantity = GREATEST(current_product_quantity - in_quantity, 0)
        WHERE ProductID = in_product_id;
    END;
    """
    execute_query(create_connection(), create_procedure_query)
    if operation == "Insert":
        # Insert Cart
        user_id = st.number_input("User ID", min_value=1, key="insert_cart_user_id")
        product_id = st.number_input("Product ID", min_value=1, key="insert_cart_product_id")
        quantity = st.number_input("Quantity", min_value=1, key="insert_cart_quantity")

        if st.button("Insert Cart"):
            add_to_cart_and_update_quantity(create_connection(), user_id, product_id, quantity)

    elif operation == "Display":
        # Display Carts
        if st.button("Display Carts"):
            display_carts_query = "SELECT * FROM Cart;"
            carts = pd.read_sql_query(display_carts_query, create_connection())
            st.dataframe(carts)

    elif operation == "Update":
        # Update Cart
        cart_id = st.number_input("Enter Cart ID to Update", min_value=1, key="update_cart_id")
        new_user_id = st.number_input("New User ID", min_value=1, key="update_cart_user_id")
        new_product_id = st.number_input("New Product ID", min_value=1, key="update_cart_product_id")
        new_quantity = st.number_input("New Quantity", min_value=1, key="update_cart_quantity")

        if st.button("Update Cart"):
            update_cart_query = "UPDATE Cart SET UserID=%s, ProductID=%s, Quantity=%s WHERE CartID=%s;"
            execute_query(create_connection(), update_cart_query, (new_user_id, new_product_id, new_quantity, cart_id))

    elif operation == "Delete":
        # Delete Cart
        cart_id_to_delete = st.number_input("Enter Cart ID to Delete", min_value=1, key="delete_cart_id")

        if st.button("Delete Cart"):
            delete_cart_query = "DELETE FROM Cart WHERE CartID=%s;"
            execute_query(create_connection(), delete_cart_query, (cart_id_to_delete,))

# Function to perform CRUD operations on the Order table
def order_crud():
    st.header("Order CRUD Operations")

    # Get or create session state
    session_state = st.session_state

    # Create Order Table
    create_order_table_query = """
    CREATE TABLE IF NOT EXISTS `Order` (
        OrderID INTEGER PRIMARY KEY AUTO_INCREMENT,
        UserID INTEGER,
        OrderDate DATETIME DEFAULT CURRENT_TIMESTAMP,
        Status TEXT,
        ShippingAddress TEXT,
        FOREIGN KEY (UserID) REFERENCES `User`(UserID)
    );
    """
    create_table(create_connection(), create_order_table_query)

    # Create function for calculating total price
    create_total_price_function_query = """
        CREATE FUNCTION IF NOT EXISTS calculate_cart_total_for_user(user_id INT)
        RETURNS DECIMAL(10, 2)
        DETERMINISTIC
        NO SQL
        BEGIN
            DECLARE total DECIMAL(10, 2);

            SELECT SUM(p.Price * c.Quantity)
            INTO total
            FROM Cart c
            JOIN Product p ON c.ProductID = p.ProductID
            WHERE c.UserID = user_id;

            SET total = IFNULL(total, 0);
            RETURN total;
        END;
    """
    execute_query(create_connection(), create_total_price_function_query)

    # Select operation
    operation = st.selectbox("Select Operation", ["Insert", "Display", "Update", "Delete"])

    if operation == "Insert":
        # Insert Order
        user_id = st.number_input("User ID", min_value=1, key="insert_order_user_id")
        status = st.text_input("Status", key="insert_order_status")
        shipping_address = st.text_input("Shipping Address", key="insert_order_shipping_address")

        if st.button("Insert Order"):
            # Insert with an auto-incremented OrderID
            insert_order_query = "INSERT INTO `Order` (UserID, Status, ShippingAddress) VALUES (%s, %s, %s);"
            execute_query(create_connection(), insert_order_query, (user_id, status, shipping_address))

    elif operation == "Display":
        # Display Orders
        if st.button("Display Orders"):
                display_orders_query = """
                SELECT OrderID, UserID, OrderDate, Status, ShippingAddress,
                    calculate_cart_total_for_user(UserID) as CalculatedTotalAmount
                FROM `Order`;
                """
                orders = pd.read_sql_query(display_orders_query, create_connection())
                
                st.dataframe(orders)

    elif operation == "Update":
        # Update Order
        order_id = st.number_input("Enter Order ID to Update", min_value=1, key="update_order_id")
        new_user_id = st.number_input("New User ID", min_value=1, key="update_order_user_id")
        new_total_amount = st.number_input("New Total Amount", min_value=0.0, key="update_order_total_amount")
        new_status = st.text_input("New Status", key="update_order_status")
        new_shipping_address = st.text_input("New Shipping Address", key="update_order_shipping_address")

        if st.button("Update Order"):
            update_order_query = "UPDATE `Order` SET UserID=%s, TotalAmount=%s, Status=%s, ShippingAddress=%s WHERE OrderID=%s;"
            execute_query(create_connection(), update_order_query, (new_user_id, new_total_amount, new_status, new_shipping_address, order_id))

    elif operation == "Delete":
        # Delete Order
        order_id_to_delete = st.number_input("Enter Order ID to Delete", min_value=1, key="delete_order_id")

        if st.button("Delete Order"):
            delete_order_query = "DELETE FROM `Order` WHERE OrderID=%s;"
            execute_query(create_connection(), delete_order_query, (order_id_to_delete,))

# Function to perform CRUD operations on the Product table
def product_crud():
    st.header("Product CRUD Operations")

    # Get or create session state
    session_state = st.session_state

    # Create Product Table
    create_product_table_query = """
    CREATE TABLE IF NOT EXISTS Product (
        ProductID INTEGER PRIMARY KEY AUTO_INCREMENT,
        Name TEXT NOT NULL,
        Price REAL NOT NULL,
        Description TEXT,
        StockQuantity INTEGER,
        CategoryID INTEGER,
        Brand TEXT,
        Size TEXT,
        Color TEXT,
        FOREIGN KEY (CategoryID) REFERENCES Category(CategoryID)
    );
    """
    create_table(create_connection(), create_product_table_query)

    # Select operation
    operation = st.selectbox("Select Operation", ["Insert", "Display", "Update", "Delete"])

    if operation == "Insert":
        # Insert Product
        name = st.text_input("Name", key="insert_product_name")
        price = st.number_input("Price", min_value=0.0, key="insert_product_price")
        description = st.text_input("Description", key="insert_product_description")
        stock_quantity = st.number_input("Stock Quantity", min_value=0, key="insert_product_stock_quantity")
        category_id = st.number_input("Category ID", min_value=1, key="insert_product_category_id")
        brand = st.text_input("Brand", key="insert_product_brand")
        size = st.text_input("Size", key="insert_product_size")
        color = st.text_input("Color", key="insert_product_color")

        if st.button("Insert Product"):
            # Insert with an auto-incremented ProductID
            insert_product_query = "INSERT INTO Product (Name, Price, Description, StockQuantity, CategoryID, Brand, Size, Color) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);"
            execute_query(create_connection(), insert_product_query, (name, price, description, stock_quantity, category_id, brand, size, color))

    elif operation == "Display":
        # Display Products
        if st.button("Display Products"):
            display_products_query = "SELECT * FROM Product;"
            products = pd.read_sql_query(display_products_query, create_connection())
            st.dataframe(products)

    elif operation == "Update":
        # Update Product
        product_id = st.number_input("Enter Product ID to Update", min_value=1, key="update_product_id")
        new_name = st.text_input("New Name", key="update_product_name")
        new_price = st.number_input("New Price", min_value=0.0, key="update_product_price")
        new_description = st.text_input("New Description", key="update_product_description")
        new_stock_quantity = st.number_input("New Stock Quantity", min_value=0, key="update_product_stock_quantity")
        new_category_id = st.number_input("New Category ID", min_value=1, key="update_product_category_id")
        new_brand = st.text_input("New Brand", key="update_product_brand")
        new_size = st.text_input("New Size", key="update_product_size")
        new_color = st.text_input("New Color", key="update_product_color")

        if st.button("Update Product"):
            update_product_query = "UPDATE Product SET Name=%s, Price=%s, Description=%s, StockQuantity=%s, CategoryID=%s, Brand=%s, Size=%s, Color=%s WHERE ProductID=%s;"
            execute_query(create_connection(), update_product_query, (new_name, new_price, new_description, new_stock_quantity, new_category_id, new_brand, new_size, new_color, product_id))

    elif operation == "Delete":
        # Delete Product
        product_id_to_delete = st.number_input("Enter Product ID to Delete", min_value=1, key="delete_product_id")

        if st.button("Delete Product"):
            delete_product_query = "DELETE FROM Product WHERE ProductID=%s;"
            execute_query(create_connection(), delete_product_query, (product_id_to_delete,))

# Function to perform CRUD operations on the Category table
def category_crud():
    st.header("Category CRUD Operations")

    # Get or create session state
    session_state = st.session_state

    # Create Category Table
    create_category_table_query = """
    CREATE TABLE IF NOT EXISTS Category (
        CategoryID INTEGER PRIMARY KEY AUTO_INCREMENT,
        Name TEXT NOT NULL,
        Description TEXT
    );
    """
    create_table(create_connection(), create_category_table_query)

    # Select operation
    operation = st.selectbox("Select Operation", ["Insert", "Display", "Update", "Delete"])

    if operation == "Insert":
        # Insert Category
        name = st.text_input("Name", key="insert_category_name")
        description = st.text_input("Description", key="insert_category_description")

        if st.button("Insert Category"):
            # Insert with an auto-incremented CategoryID
            insert_category_query = "INSERT INTO Category (Name, Description) VALUES (%s, %s);"
            execute_query(create_connection(), insert_category_query, (name, description))

    elif operation == "Display":
        # Display Categories
        if st.button("Display Categories"):
            display_categories_query = "SELECT * FROM Category;"
            categories = pd.read_sql_query(display_categories_query, create_connection())
            st.dataframe(categories)

    elif operation == "Update":
        # Update Category
        category_id = st.number_input("Enter Category ID to Update", min_value=1, key="update_category_id")
        new_name = st.text_input("New Name", key="update_category_name")
        new_description = st.text_input("New Description", key="update_category_description")

        if st.button("Update Category"):
            update_category_query = "UPDATE Category SET Name=%s, Description=%s WHERE CategoryID=%s;"
            execute_query(create_connection(), update_category_query, (new_name, new_description, category_id))

    elif operation == "Delete":
        # Delete Category
        category_id_to_delete = st.number_input("Enter Category ID to Delete", min_value=1, key="delete_category_id")

        if st.button("Delete Category"):
            delete_category_query = "DELETE FROM Category WHERE CategoryID=%s;"
            execute_query(create_connection(), delete_category_query, (category_id_to_delete,))

# Function to perform CRUD operations on the User_Uploads table
def user_uploads_crud():
    st.header("User_Uploads CRUD Operations")

    # Get or create session state
    session_state = st.session_state

    # Create User_Uploads Table
    create_user_uploads_table_query = """
    CREATE TABLE IF NOT EXISTS User_Uploads (
        UploadID INTEGER PRIMARY KEY AUTO_INCREMENT,
        UserID INTEGER,
        ProfileImageFilename TEXT,
        ProfileImageFileType TEXT,
        UploadDate DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (UserID) REFERENCES User(UserID)
    );
    """
    create_table(create_connection(), create_user_uploads_table_query)

    # Select operation
    operation = st.selectbox("Select Operation", ["Insert", "Display", "Update", "Delete"])

    if operation == "Insert":
        # Insert User_Upload
        user_id = st.number_input("User ID", min_value=1, key="insert_user_upload_user_id")
        profile_image_file = st.file_uploader("Upload Profile Image", type=["jpg", "jpeg", "png"], key="insert_user_upload_file")

        if st.button("Insert User_Upload") and profile_image_file:
            # Save the uploaded image
            image_bytes = profile_image_file.read()
            image_extension = profile_image_file.type.split("/")[-1]
            profile_image_filename = f"{user_id}_profile_image.{image_extension}"
            with open(profile_image_filename, "wb") as f:
                f.write(image_bytes)

            # Insert with an auto-incremented UploadID
            insert_user_upload_query = "INSERT INTO User_Uploads (UserID, ProfileImageFilename, ProfileImageFileType) VALUES (%s, %s, %s);"
            execute_query(create_connection(), insert_user_upload_query, (user_id, profile_image_filename, image_extension))

    elif operation == "Display":
        # Display User_Uploads with images
        if st.button("Display User_Uploads"):
            display_user_uploads_query = "SELECT * FROM User_Uploads;"
            user_uploads = pd.read_sql_query(display_user_uploads_query, create_connection())
            st.dataframe(user_uploads)

            # Display images
            for index, row in user_uploads.iterrows():
                image_path = row["ProfileImageFilename"]

                # Create two columns
                col1, col2 = st.columns(2)

                # Display image in the left column
                col1.image(image_path, caption="", width=100)

                # Display caption in the right column
                col2.write(f"UserID: {row['UserID']}, UploadID: {row['UploadID']}")

    elif operation == "Update":
        # Update User_Upload
        upload_id = st.number_input("Enter Upload ID to Update", min_value=1, key="update_user_upload_id")
        new_user_id = st.number_input("New User ID", min_value=1, key="update_user_upload_user_id")
        new_profile_image_file = st.file_uploader("New Profile Image", type=["jpg", "jpeg", "png"], key="update_user_upload_file")

        if st.button("Update User_Upload") and new_profile_image_file:
            # Save the uploaded image
            image_bytes = new_profile_image_file.read()
            image_extension = new_profile_image_file.type.split("/")[-1]
            new_profile_image_filename = f"{new_user_id}_profile_image.{image_extension}"
            with open(new_profile_image_filename, "wb") as f:
                f.write(image_bytes)

            # Update User_Upload
            update_user_upload_query = "UPDATE User_Uploads SET UserID=%s, ProfileImageFilename=%s, ProfileImageFileType=%s WHERE UploadID=%s;"
            execute_query(create_connection(), update_user_upload_query, (new_user_id, new_profile_image_filename, image_extension, upload_id))

    elif operation == "Delete":
        # Delete User_Upload
        upload_id_to_delete = st.number_input("Enter Upload ID to Delete", min_value=1, key="delete_user_upload_id")

        if st.button("Delete User_Upload"):
            delete_user_upload_query = "DELETE FROM User_Uploads WHERE UploadID=%s;"
            execute_query(create_connection(), delete_user_upload_query, (upload_id_to_delete,))

# Run the application
if __name__ == "__main__":
    st.title("Fashionify")

    # Choose the table for CRUD operations
    table_choice = st.selectbox("Select Table", ["User", "Cart", "Order", "Product", "Category", "User_Uploads"])

    if table_choice == "User":
        user_crud()
    elif table_choice == "Cart":
        cart_crud()
    elif table_choice == "Order":
        order_crud()
    elif table_choice == "Product":
        product_crud()
    elif table_choice == "Category":
        category_crud()
    elif table_choice == "User_Uploads":
        user_uploads_crud()
