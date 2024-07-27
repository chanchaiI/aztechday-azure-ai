# Motor Roadside assistance application
---

## Content
- [Overview](#overview)
- [Run Streamlit UI](#run-streamlit-ui)
    - [Stop Streamlit UI](#stop-streamlit-ui)

## Overview

A Motor Roadside Assistance application that provides a platform for users to request assistance for their vehicles. The application is built using the following technologies:
- Streamlit UI
- Azure AI Services

## Run Streamlit UI

To isolate our Streamlit application dependencies and for ease of deployment, we use the setup-streamlit-env.sh shell script to create a virtual Python environment with the requirements installed.

1. Before you run the shell script, navigate to the directory where you have the setup-streamlit-env.sh file and run the following command:

```sh
cd ui/streamlit
chmod +x setup-streamlit-env.sh
```

2. Run the shell script to activate the virtual Python environment with the required dependencies:

```sh 
source ./setup-streamlit-env.sh
```

3. Run your Streamlit application and begin testing in your local web browser:

```sh 
streamlit run azure_agent_streamlit.py
```

### Stop Streamlit UI

1. Stop the application by pressing `Ctrl + C` in the terminal where the Streamlit application is running.

2. Run the following command to deactivate the virtual Python environment:

```sh
deactivate
```

## References

- Streamlit documentation: [Streamlit documentation](https://docs.streamlit.io/)
For more information on Streamlit, visit the [Streamlit documentation](https://docs.streamlit.io/).
Information about building chatbot GUI via StreamLit, visit the [Streamlit Chatbot GUI documentation](https://docs.streamlit.io/develop/tutorials/llms/build-conversational-apps#build-a-simple-chatbot-gui-with-streaming).
Gallery of Streamlit applications, visit the [Streamlit Gallery](https://streamlit.io/gallery?category=llms).

And also, for more information on Azure AI Services, visit the [Azure AI Services documentation](https://docs.microsoft.com/en-us/azure/cognitive-services/).

```