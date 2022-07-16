from __future__ import annotations

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from database_tools import create_db_connection, execute_query

from dotenv import load_dotenv
import os

load_dotenv()


class Store:
    """ A supported e-store.

    NOTE: This is an abstract class. DO NOT initialize this class.
    """
    def update_inventory(self, driver: webdriver.Safari) -> None:
        """ Drop the current 'STORENAME' table in the database defined in .env, and create a new one with all PC
        components sold at this store. The table will contain a unique identifier corresponding to the item, the item's
        name, the item's current price, the item's discount (if any), if the item is in stock, and a URL linking to the
        item's page on the BestBuy website.
        """
        raise NotImplementedError


class BestBuy(Store):
    def update_inventory(self, driver: webdriver.Safari) -> None:
        """ Drop the current 'best_buy' table in the database defined in .env, and create a new one with all PC
        components sold at BestBuy (and sold only by BestBuy and not marketplace sellers). The table will contain a
        unique identifier corresponding to the item, the item's name, the item's current price, the item's discount (if
        any), if the item is in stock, and a URL linking to the item's page on the BestBuy website.
        """
        # === DATABASE SETUP ===
        # create a connection to the database defined in .env
        connection = create_db_connection(os.environ.get("database_host"),
                                          os.environ.get("database_username"),
                                          os.environ.get("database_password"),
                                          os.environ.get("database_name"))
        # drop the current best_buy table
        execute_query(connection, 'DROP TABLE IF EXISTS `best_buy`')
        # create a new table with columns described in the method description
        execute_query(connection,
                      'CREATE TABLE `pcpartsbotdb`.`best_buy` (`id` INT NOT NULL AUTO_INCREMENT,`name` VARCHAR(100) NULL,`price` FLOAT NULL,`sale_amount` FLOAT NULL,`in_stock` TINYINT NULL,`link` VARCHAR(1000) NULL, PRIMARY KEY (`id`), UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE);')

        execute_query(connection, 'ALTER TABLE `pcpartsbotdb`.`best_buy` ADD UNIQUE INDEX `name_UNIQUE` (`name` ASC) VISIBLE;')
        # === DATA SCRAPING AND INVENTORY BUILDING ===
        # navigate to the BestBuy website on the PC components category page and with filter for the highest rated items
        driver.get('https://www.bestbuy.ca/en-ca/category/pc-components/20374?path=category%253AComputers%2B%2526%2BTablets%253Bcategory%253APC%2BComponents%253Bsoldandshippedby0enrchstring%253ABest%2BBuy&sort=highestRated&page=1')
        driver.maximize_window()
        driver.implicitly_wait(10)

        # this loop will iterate through all 12 pages (the number of pages containing every PC component at the time of
        # writing) and will extract the details of every product on each page.
        i = 1
        page_number = 1
        while page_number != 12:
            driver.implicitly_wait(10)
            try:
                # get the name of the current product
                name = driver.find_element(By.XPATH,
                                           f'//*[@id="root"]/div/div[2]/div[1]/div/main/div[1]/div[4]/div[2]/div[2]/ul/div/div[{i}]/div/a/div/div/div[2]/div[1]').text
                # get the price of the current product (original format is a string "$XXX,XXX", so the dollar sign and commas are dropped)
                price = float(driver.find_element(By.XPATH,
                                            f'//*[@id="root"]/div/div[2]/div[1]/div/main/div[1]/div[4]/div[2]/div[2]/ul/div/div[{i}]/div/a/div/div/div[2]/div[3]/span[1]/div/div').text[1:].replace(',', ''))
                # get the discount on the current product
                try:
                    # if a sale exists, format the string ("SAVE $XXX,XXX")
                    sale_amount = float(driver.find_element(By.XPATH,
                                                      f'//*[@id="root"]/div/div[2]/div[1]/div/main/div[1]/div[4]/div[2]/div[2]/ul/div/div[{i}]/div/a/div/div/div[2]/div[3]/span[2]').text[6:].replace(',', ''))
                except NoSuchElementException:
                    # if no sale exists, there is a $0.00 discount
                    sale_amount = 0.0
                try:
                    # get whether or not the current item is in stock. SQL databases use TINYINTs as booleans, so this convention is conformed to
                    in_stock = 0 if driver.find_element(By.XPATH,
                                                        f'//*[@id="root"]/div/div[2]/div[1]/div/main/div[1]/div[4]/div[2]/div[2]/ul/div/div[{i}]/div/a/div/div/div[2]/div[4]/div/p/span[2]').text == 'Sold out online' else 1
                except NoSuchElementException:
                    in_stock = 0
                # extract the URL to the details page of the current product
                link = driver.find_element(By.XPATH,
                                           f'/html/body/div[1]/div/div[2]/div[1]/div/main/div[1]/div[4]/div[2]/div[2]/ul/div/div[{i}]/div/a').get_attribute('href')
                # insert the details of the product into the table, including the id which autoincrements
                execute_query(connection,
                              f'INSERT INTO `best_buy` VALUES (DEFAULT, "{name}", {price}, {sale_amount}, {in_stock}, "{link}")')
                i += 1

            # NOTE: this except block should only execute should the name of the product be not found
            except NoSuchElementException:
                # in this case, there are no more products on the current page; move on to the next page
                page_number += 1
                i = 1  # reset i to 1 because we will be going to the first product on the new page
                driver.get(f'https://www.bestbuy.ca/en-ca/category/pc-components/20374?path=category%253AComputers%2B%2526%2BTablets%253Bcategory%253APC%2BComponents%253Bsoldandshippedby0enrchstring%253ABest%2BBuy&sort=highestRated&page={page_number}')
                driver.implicitly_wait(10)
            except TimeoutException:
                # in this case, a timeout occur (because the script takes too long to execute). Simply reload the page and continue the loop.
                driver.get(f'https://www.bestbuy.ca/en-ca/category/pc-components/20374?path=category%253AComputers%2B%2526%2BTablets%253Bcategory%253APC%2BComponents%253Bsoldandshippedby0enrchstring%253ABest%2BBuy&sort=highestRated&page={page_number}')



