from config import WooConfig
from logging_config import setup_logger
from woo_client import WooClient
from pipelines.orders_pipeline import OrdersPipeline
from pipelines.products_pipeline import ProductsPipeline
from pipelines.customers_pipeline import CustomersPipeline

#print("main.py loaded")

logger = setup_logger()


def run_pipeline(pipeline):
    logger.info("Pipeline started | entity=%s", pipeline.entity_name)

    pipeline.extract()
    pipeline.transform()
    pipeline.load()

    logger.info("Pipeline finished | entity=%s", pipeline.entity_name)


def main():
    print("main() started")
    logger.info("Application started")

    try:
        config = WooConfig()
        print("config loaded")

        client = WooClient(config)
        print("client created")

        client.test_connection()
        print("connection test passed")

        orders_pipeline = OrdersPipeline(client, config)
        run_pipeline(orders_pipeline)

        products_pipeline = ProductsPipeline(client, config)
        run_pipeline(products_pipeline)

        customers_pipeline = CustomersPipeline(client, config)
        run_pipeline(customers_pipeline)

        logger.info("Application finished successfully")
        print("application finished")

    except Exception as e:
        logger.exception("Application failed")
        print(f"ERROR: {e}")
        raise


if __name__ == "__main__":
    main()