# pylint: disable=R0201
""" Contains a LegoRestockBot class to create and send Telegram messages for product updates """

import telegram


def price_cents_to_str(cents: int) -> str:
    """Helper to convert cents to a decimal representation in Euro"""
    return f"{float(cents) / 100.0:.2f}".replace(".", ",")


class LegoRestockBot:
    """Class to create and send Lego update messages"""

    def __init__(self, token: str, channel_id: str) -> None:
        """Instantiante the telegram.Bot with the Telegram bot token"""
        self.bot = telegram.Bot(token=token)
        self.channel_id = channel_id

    def create_message_available(
        self,
        product_id: int,
        product_name: str,
        product_url: str,
        product_price_cents: int,
    ) -> str:
        """
        Create a message about an available product

        Possible HTML tags to be used in Telegram:
        <b>bold</b>, <strong>bold</strong>
        <i>italic</i>, <em>italic</em>
        <a href="http://www.example.com/">inline URL</a>
        <code>inline fixed-width code</code>
        <pre>pre-formatted fixed-width code block</pre>"""

        # "🚀➡️"
        return (
            f"🚀 <b>{product_name}</b> #{product_id} 🚀\n\n <b>{product_name}</b> ist wieder für \
            {price_cents_to_str(product_price_cents)}€ verfügbar!\n\n➡️➡️ "
            + f'Zum Lego Shop <a href="{product_url}">#{product_id}: {product_name}</a>'
        )

    def create_message_reorder(
        self,
        product_id: int,
        product_name: str,
        product_url: str,
    ) -> str:
        """
        Create a message about a product that can be ordered again on the lego page

        Possible HTML tags to be used in Telegram:

        <b>bold</b>, <strong>bold</strong>
        <i>italic</i>, <em>italic</em>
        <a href="http://www.example.com/">inline URL</a>
        <code>inline fixed-width code</code>
        <pre>pre-formatted fixed-width code block</pre>"""

        # "🚀➡️"
        return (
            f"🚀  <b>{product_name}</b> #{product_id} 🚀\n\n Für <b>{product_name}</b> sind wieder \
            Nachbestellungen möglich!\n\n➡️➡️ "
            + f'Zum Lego Shop <a href="{product_url}">#{product_id}: {product_name}</a>'
        )

    def send_html_message_to_channel(self, html_str: str):
        """Sends a message to the telegram channel in HTML mode"""
        self.bot.send_message(text=html_str, chat_id=self.channel_id, parse_mode="html")
