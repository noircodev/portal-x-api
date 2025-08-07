The recommended formula for calculating the number of Gunicorn workers is:

$$
workers = 2 \times \text{CPU cores} + 1
$$

For a **single-core CPU**:

$$
workers = 2 \times 1 + 1 = 3
$$

So, your `--workers` value should be **3** (which is what you originally had).

### **Alternative for Low Memory Systems**:

If your server has very **limited RAM** (e.g., ≤ 512MB), you may want to reduce it to **2** workers to prevent excessive memory usage:

```ini
--workers 2
```
