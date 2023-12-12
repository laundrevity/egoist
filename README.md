# Egoist

Welcome to Egoist, a modern AI tool management system designed to enhance the way we interact with software tools. This project draws upon the strengths of OpenAI's GPT models and a bespoke toolkit to execute file, code, and HTTP operations effectively.

## Features

- Executing Python code with access to a dynamic toolkit instance.
- Performing comprehensive file operations including creation, deletion, and modification.
- Sending and receiving HTTP requests for GET and POST methods.
- Running shell commands with output capture for both stdout and stderr.
- Snapping code together with options for line numbering and including infrastructure files.

## Usage

Egoist is designed to be user-friendly and can be easily integrated with your current workflow to automate various tasks. Begin by setting up your environment and then use the provided example codes to start leveraging the power of AI-driven automation.

## Setup

Clone the repository and install the required dependencies:

```bash
git clone https://github.com/your-username/egoist.git
cd egoist
pip install -r requirements.txt
```

For extra isolation, it is recommended to run the tool within a Docker container, which can be started and entered like this:
```bash
docker compose up -d --build
docker compose exec app bash
```

## Running Egoist

To start the Egoist AI tool management system, simply use the following command:

```bash
python main.py "Your initial prompt here"
```

## Contributing

Contributions are welcome! If you have a suggestion or improvement, feel free to fork the repository and create a pull request.

## License

Distributed under the MIT License. See `LICENSE` for more information.

## Contact

Conor Mahany: conor@mahany.io<br>
Project Link: [https://github.com/laundrevity/egoist](https://github.com/laundrevity/egoist)