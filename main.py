# from transformers import pipeline
# import torch

# # Check if gpu is available
# print(torch.cuda.is_available())
# print(torch.cuda.get_device_name(0))

# model = pipeline(task="summarization", model="facebook/bart-large-cnn", device="0")
# response = model("text to summarize")
# print(response)

# prompt = """Given the following meeting transcript, extract and categorize the key tasks into the following categories: Events, To-Do List, Action Items, and Meetings. Each category should contain specific details, deadlines (if mentioned), and assigned persons (if applicable). Present the output in a structured format for easy integration into a to-do planner and calendar system.

# Output Format:

# Events: (List all upcoming events, their date/time, and any relevant details)

# Event Name: [Event title]
# Date & Time: [Date & Time]
# Description: [Brief description]
# Responsible Person(s): [Name(s)]
# To-Do List: (List all general tasks that need to be completed, with deadlines if provided)

# Task: [Task description]
# Deadline: [Date if mentioned]
# Assigned To: [Person or Team]
# Action Items: (List tasks that require specific follow-up actions, including deadlines and responsible persons)

# Action Item: [Action description]
# Deadline: [Date if mentioned]
# Responsible Person(s): [Name(s)]
# Meetings: (List all upcoming meetings with relevant details)

# Meeting Title: [Meeting name]
# Date & Time: [Date & Time]
# Participants: [List of attendees]
# Agenda: [Brief agenda of the meeting]
# Ensure that all extracted tasks, events, and meetings are clear and well-structured for easy integration into a planner or calendar system"""


import ollama


class llm_model:
    def summarize(self, conversation_string):
        prompt1 = """
            summarise the above meeting transcript. 
        """
        response = ollama.chat(
            model="gemma2:2b",
            messages=[
                {"role": "system", "content": prompt1},
                {"role": "user", "content": conversation_string},
            ],
        )
        # response = self.model(
        #     messages=[
        #         {"role": "system", "content": prompt1},
        #         {"role": "user", "content": conversation_string},
        #     ]
        # )
        result = response["message"]["content"]
        return result

    def extract(self, conversation_string):
        prompt2 = """
            /----------------------------------------/
            CONTEXT: 
            You are a bot whose function is to summarize and provide detailed insights of a given meeting conversation.

            /----------------------------------------/
            TASK:
            You are required to provide the following details. Provide them only if they are available in the provided meeting trasncript. !!NEVER HALLUCINAT OR ASSUME ANYTHING!!

            1. List all the events mentioned in the conversation.
            2. List all the tasks mentioned in the conversation.
            3. Basic meeting details (date, time, title, agenda,...).
            4. Calendar events (if any).

            /----------------------------------------/
            OUTPUT FORMAT (JSON):

            {
                "meeting_details": {
                    "date_time": "",
                    "title": "",
                    "agenda": "",
                    "participants": ""
                },
                "tasks": [
                    {
                        "task": "Finalize the pitch deck",
                        "deadline": "Monday",
                        "assigned_to": "Sarah"
                    }
                ],
                "calendar_events": [
                {
                    "event_name": "Team-building session",
                    "date_time": "Next Friday",
                    "description": "Team-building session next Friday.",
                    "responsible_person": ""
                }
                ]
            }


            /----------------------------------------/
            NOTE:
            - The output should be in JSON format.
            - Ensure that the output is structured and well-formatted.
            - Include all relevant details for each category !!Only include data if it is explicitly mentioned in the conversation else leave it empty(null)!!
            - Do not include any irrelevant information or make any assumptions.
            - Do not include any other information just need the result in json format
        """

        response = ollama.chat(
            model="gemma2:2b",
            messages=[
                {"role": "system", "content": prompt2},
                {"role": "user", "content": conversation_string},
            ],
        )
        result = response["message"]["content"]
        return result


conversation_string = """
Good morning, everyone. Let's start today's meeting by reviewing our ongoing projects. 
The marketing team is working on the new campaign, and we need the final content ready by Friday. 
John, please coordinate with the design team to ensure all visuals are completed on time. 
Next, the product team is preparing for the upcoming feature release. Sarah, can you provide an update on the testing progress? 
Moving on to events, we have a client presentation scheduled for next Wednesday, so we need the pitch deck finalized by Monday.
Also, don't forget about the team-building session next Friday—HR will send out the details by the end of the day.
Regarding the to-do list, all pending reports must be submitted by the end of the week, and everyone should update their project status in the tracker before our next meeting. 
Now, let’s assign action items: Mike, follow up with the client about their requirements; Lisa, review the budget for the upcoming quarter; and Jake, finalize the vendor contracts. 
If anyone has any roadblocks, please raise them now so we can address them. 
That covers everything for today—let’s stay on track and ensure we meet our deadlines. Thanks, everyone!
"""

# obj = llm_model()
# summary = obj.summarize(conversation_string)
# details = obj.extract_details(conversation_string)

# Output
"""
{
    "meeting_details": {
        "date_time": "Unspecified",
        "title": "Meeting Review of Ongoing Projects", 
        "agenda": "Review of ongoing projects, including marketing campaign content, feature release preparations, client presentation, team-building session, to-do list updates, and action item assignments.",
        "participants": "John, Sarah, Mike, Lisa, Jake, HR"
    },
    "tasks": [
        {
            "task": "Finalize the pitch deck",
            "deadline": "Monday",
            "assigned_to": "Sarah"
        },
        {
            "task": "Coordinate with the design team for visuals completion",
            "deadline": "Unspecified",
            "assigned_to": "John"
        },
        {
            "task": "Update project status in tracker",
            "deadline": "Before next meeting",
            "assigned_to": "All participants"
        },
        {
            "task": "Follow up with the client about their requirements",
            "deadline": "Unspecified",
            "assigned_to": "Mike"
        },
        {
            "task": "Review the budget for the upcoming quarter",
            "deadline": "Unspecified",
            "assigned_to": "Lisa"
        },
        {
            "task": "Finalize vendor contracts",
            "deadline": "Unspecified",
            "assigned_to": "Jake"
        }
    ],
    "calendar_events": [
        {
            "event_name": "Client Presentation",
            "date_time": "Next Wednesday",
            "description": "Client presentation scheduled for next Wednesday.",
            "responsible_person": ""
        },
        {
            "event_name": "Team-building session",
            "date_time": "Next Friday",
            "description": "Team-building session will be held next Friday.",
            "responsible_person": "HR"
        }
    ]
}
```

**Explanation of the Output:**

* **Meeting Details:** The JSON includes basic information about the meeting. We have a "date_time" field that should be filled with details provided in the transcript.
* **Tasks:** A list of tasks is included, including deadlines and assigned individuals.
* **Calendar Events:**  We have entries for the client presentation and team-building session.


**Notes:**

* The meeting date and time are not explicitly mentioned in the transcript, so we've added "Unspecified". It should be filled with the actual information once you provide it to me.
* If any other details (like an agenda or participants list) were present in the transcript, I would include them in the output format, but this particular example has only provided essential meeting details.
"""
