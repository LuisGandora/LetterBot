
import ollama



messages = [{"role": "system", "content": "You are a precise AI that compiles a reviews off the website Letterboxd to create comprehensive, but spoiler-free overviews of movies."},
            {"role": "system", "content": "You are a precise AI agent. You will be given data based on the prompt the user gives you from data collected off of Letterboxd and will output a result based on this data."},
            {"role": "system", "content": "You CANNNOT under ANY cirumstances make up information."},
            {"role": "system", "content": "If user says \"a\" movie, only list one. NEVER list more than 10 unless explicitly told to do so."},
            {"role": "system", "content": "ALWAYS follow the rules."}
            ]

def letterboxd_bot(prompt):
    model_name = 'mistral:7b'

    messages.append({"role": "user", "content": prompt})

    result = ollama.chat(model=model_name, messages=messages)
    response = result.message.content

    print(response)

    messages.append({"role": "assistant", "content": response})


def main():

    while True:
        prompt = input("Ask a question (input exit to quit): ")
        if prompt == "exit":
            exit(0)
        else:
            letterboxd_bot(prompt)


if __name__ == "__main__":
    main()
