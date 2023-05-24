# Ask PDF Demo

For details about using this service, see [details.md](details.md)



## Building and Publishing

**Note:** Get and OpenAI API key and  then:

1. Clone this repo with:

```bash
git clone https://github.com/iportilla/ask-pdf.git
```

2. Copy .env.sample to .env with:

```bash
cp .env.sample .env
```

3. Update .env with *OpenAI* settings:

```bash
API_KEY="YOUR_API_KEY"
```

4. Run

```bash
make clean
make build
make run
```