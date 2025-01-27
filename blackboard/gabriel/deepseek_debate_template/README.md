> [!NOTE]  
> This is still super rough, I'll probably just work on a seperate script that mimicks the actual structure of the chinese papers.  
> ~ Gabriel  

# DeepSeek debate template

Rough prompt and logging template for generating a debate between 2 models, called via API requests to DeepSeek API.

## Usage

Place your DeepSeek API key into a `.env` file.

```env
DEEPSEEK_API_KEY=<the_api_key>
```

Then run.

```console
$ make config
$ make 
```