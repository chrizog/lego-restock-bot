import telegram


def price_cents_to_str(cents: int) -> str:
    return ("{:.2f}".format(float(cents) / 100.0)).replace(".", ",")


class LegoRestockBot:
    def __init__(self, token: str, channel_id: str) -> None:
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
        Possible HTML tags:
        <b>bold</b>, <strong>bold</strong>
        <i>italic</i>, <em>italic</em>
        <a href="http://www.example.com/">inline URL</a>
        <code>inline fixed-width code</code>
        <pre>pre-formatted fixed-width code block</pre>"""

        # "🚀➡️"
        return '🚀 <b>{}</b> #{} 🚀\n\n <b>{}</b> ist wieder für {}€ verfügbar!\n\n➡️➡️ Zum Lego Shop <a href="{}">#{}: {}</a>'.format(
            product_name,
            product_id,
            product_name,
            price_cents_to_str(product_price_cents),
            product_url,
            product_id,
            product_name,
        )

    def create_message_reorder(
        self,
        product_id: int,
        product_name: str,
        product_url: str,
    ) -> str:
        """
        Possible HTML tags:
        <b>bold</b>, <strong>bold</strong>
        <i>italic</i>, <em>italic</em>
        <a href="http://www.example.com/">inline URL</a>
        <code>inline fixed-width code</code>
        <pre>pre-formatted fixed-width code block</pre>"""

        # "🚀➡️"
        return '🚀  <b>{}</b> #{} 🚀\n\n Für <b>{}</b> sind wieder Nachbestellungen möglich!\n\n➡️➡️ Zum Lego Shop <a href="{}">#{}: {}</a>'.format(
            product_name,
            product_id,
            product_name,
            product_url,
            product_id,
            product_name,
        )

    def send_html_message_to_channel(self, html_str: str):
        self.bot.send_message(text=html_str, chat_id=self.channel_id, parse_mode="html")
