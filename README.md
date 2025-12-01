# freekassa api client
## Intallation

```sh
pip install freekassa-client
```

## Usage

### Generate link payment

```python
client = FreeKassaClient(
    merchant_id=123456789,
    secret_word_1='secret1',
    secret_word_2='secret2',
    api_key='api_key'
)
payment_link = client.ui_create_order(
    amount=Decimal(1000), currency='USD', payment_id='payment_id'
)
```

### Check payment

```python
# yours view.py
def some_view(request, *args, **kwargs):
    ...
    verified = client.verify_notify(amount, order_id, sign)
    ...
```