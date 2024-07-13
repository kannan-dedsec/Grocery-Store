from string import Template
from datetime import date


OPERATORS = {1:" = ",2:" != ",3:" IN ",4:" NOT IN ",5:" like "}
PRODUCT_COUNT_STATS_LIMIT = 4
PRODUCT_SELLING_STATS_LIMIT = 4
CATEGORY_COUNT_STATS_LIMIT = 4
CATEGORY_SELLING_STATS_LIMIT = 4
DATABASE_FILE = "database/groceryDB.db"
FILE_PATH_TO_TABLES_JSON = "database/tables.json"
LOG_FILE = "logs/serverLog-" + date.today().strftime("%d_%m_%Y")
LOGGER_FORMAT = '%(asctime)s - %(message)s'
ADD_UNIT_TEMPLATE = Template('INSERT INTO units (unit_id,unit_name) VALUES ("$unit_id","$unit_name");');
ADD_CATEGORY_TEMPLATE = Template('INSERT INTO categories (category_id,category_name) VALUES ("$category_id","$category_name");');
DROP_TABLE_TEMPLATE = Template("DROP TABLE IF EXISTS $table_name ;");
DEFAULT_UNITS = ["inch", "GB", "liter", "cubic feet", "watt", "kilowatt", "S", "M", "L", "XL", "centimeter", "US size", "UK size", "EU size", "grams", "kilogram", "ounce", "pound", "milliliter", "gallon", "page", "file size", "hour", "minute", "feet", "piece", "pack", "fluid ounce", "miles per gallon", "liters per 100 kilometers", "others"]
DEFAULT_CATEGORIES = ["Electronics", "Phones & Accessories", "Computers & Laptops", "Cameras & Camcorders", "Audio & Headphones", "TVs & Home Theater", "Video Games & Consoles", "Fashion", "Men's Clothing", "Women's Clothing", "Kids & Baby Clothing", "Shoes", "Jewelry & Watches", "Bags & Accessories", "Home & Furniture", "Furniture", "Bedding & Bath", "Kitchen & Dining", "Home Decor", "Appliances", "Home Improvement", "Beauty & Personal Care", "Skincare", "Makeup", "Haircare", "Fragrances", "Personal Care & Hygiene", "Sports & Outdoors", "Exercise & Fitness", "Outdoor Recreation", "Sports Equipment", "Camping & Hiking", "Cycling", "Team Sports", "Toys & Games", "Toys for Kids", "Board Games & Puzzles", "Action Figures & Dolls", "Educational Toys", "Building Blocks & Construction Sets", "Groceries", "Fresh Produce", "Dairy & Eggs", "Meat & Seafood", "Pantry Staples", "Beverages", "Snacks & Sweets", "Books & Stationery", "Books", "Notebooks & Journals", "Pens & Writing Instruments", "Office Supplies", "Health & Wellness", "Vitamins & Supplements", "Fitness Supplements", "Natural & Herbal Remedies", "Medical & Health Equipment", "Automotive", "Car Accessories", "Car Parts", "Tires & Wheels", "Automotive Tools"]
PRAGMA_QUERY = "PRAGMA foreign_keys=ON;"
INSERT_TEMPLATE = Template("INSERT INTO $table_name ($columns) VALUES ($values);");
DELETE_TEMPLATE = Template('DELETE FROM $table_name WHERE $clause;');
READ_TEMPLATE = Template('SELECT $columns FROM $table_name WHERE $clause;');
READ_ALL_TEMPLATE = Template('SELECT $columns FROM $table_name;');
READ_ALL_STORE_TEMPLATE = Template("SELECT $columns FROM $table_name WHERE store_id = '$store_id' ORDER BY $order_by DESC ;");
ALL_PRODUCTS_QUERY = Template("select t1.item_id, t1.item_name,t1.price,t1.quantity,t2.category_name,t3.unit_name,t4.store_name,t3.unit_id,t2.category_id  from items as t1 inner join categories as t2  inner join units as t3 inner join stores as t4 on (t1.category_id  = t2.category_id) and (t1.unit = t3.unit_id) and (t1.store_id = t4.store_id) where t1.quantity >= 0 and t4.store_id like '%$store_id%' and t1.item_name like '%$search%' $filter ;")
UPDATE_TEMPLATE = Template('UPDATE $table_name SET $set_values WHERE $clause;');
CATEGORYVSCOUNT = Template("SELECT category_name, COUNT(item_id) AS item_count FROM items inner join categories on (categories.category_id  = items.category_id ) where items.category_id is not NULL and items.store_id = '$store_id' GROUP BY items.category_id ORDER BY item_count DESC;")
PRODUCTVSSELLING = Template("SELECT items.item_name, SUM(solddata.quantity) AS item_quantity FROM solddata INNER JOIN items on (solddata.item_id = items.item_id) where solddata.store_id = '$store_id'  GROUP BY solddata.item_id ORDER BY item_quantity DESC;")
CATEGORYVSSELLING = Template("SELECT categories.category_name, SUM(solddata.quantity) AS item_quantity FROM solddata INNER JOIN items INNER JOIN categories on (solddata.item_id = items.item_id) and (items.category_id = categories.category_id)  GROUP BY items.category_id ORDER BY item_quantity DESC;")
TOTAL_REVENUE = Template("SELECT sum(total_price) from solddata where store_id = '$store_id';")
TOTAL_SELLING = Template("SELECT count(user_id) from solddata where store_id = '$store_id';")
TOTAL_PRODUCTS = Template("SELECT count(item_id) from items where store_id = '$store_id';")
TOTAL_CATEGORIES = Template("SELECT count(category_id) from categories where store_id = '$store_id';")
TOTAL_CUSTOMERS = Template("SELECT COUNT(DISTINCT user_id) AS unique_item_count FROM solddata where store_id = '$store_id';")
TOTAL_CART_PRICE = Template("select SUM(t1.total_price) from carts as t1 inner join cartvsusers as t2 on  (t1.cart_id = t2.cart_id ) where t2.user_id = '$user_id';")
CART_QUERY = Template("SELECT t1.cart_id , t1.item_id , t1.count, t1.price , t1.total_price , t2.item_name,t3.category_name ,t4.unit_name  from carts as t1 INNER JOIN items as t2 INNER JOIN categories as t3 INNER JOIN units as t4  on (t1.item_id = t2.item_id ) and (t2.category_id = t3.category_id) and (t2.unit = t4.unit_id) where cart_id ='$cart_id' ; ")
