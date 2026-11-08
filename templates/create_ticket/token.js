const token = window.location.search.substring(1);

if (token != "" && token != null) {
    fetch(`/api/get_server_info_by_jwt?token=${token}`)
        .then(async response => {
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error);
            }

            return data;
        })
        .then(data => {
            const channelSelect = document.getElementById('channel');
            const feedbackChannelSelect = document.getElementById('feedback_channel');

            channelSelect.innerHTML = '';

            data.text_channels.forEach(element => {
                const newOption = document.createElement('option');
                newOption.value = element.id;
                newOption.text = element.name;
                channelSelect.appendChild(newOption);

                const feedbackOption = document.createElement('option');
                feedbackOption.value = element.id;
                feedbackOption.text = element.name;
                feedbackChannelSelect.appendChild(feedbackOption);
            });


            const roleSelect = document.getElementById('roles_to_mark');

            roleSelect.innerHTML = '';

            data.roles.forEach(element => {
                const newOption = document.createElement("option");

                newOption.value = element.id;
                newOption.text = element.name;

                roleSelect.appendChild(newOption);
            });
        })
        .catch(err => {
            document.body.innerHTML = `<h1>Error: ${err.message}</h1>`;
        });
} else {
    document.body.innerHTML = "<h1>Error: Invalid token</h1>";
}

function send_ticket_config() {
    const channelSelect = document.getElementById('channel');
    const channelId = channelSelect ? String(channelSelect.value) : null;

    const feedbackChannelSelect = document.getElementById('feedback_channel');
    const feedbackChannelId = channelSelect ? String(feedbackChannelSelect.value) : null;

    const roleSelect = document.getElementById('roles_to_mark');
    const roleId = roleSelect ? String(roleSelect.value) : null;

    let options = [];

    document.querySelectorAll("#options-container .option-item").forEach((option) => {
        options.push({
            emoji: option.querySelector(".opt-emoji").value,
            title: option.querySelector(".opt-label").value,
            description: option.querySelector(".opt-description").value,
            welcome_message: option.querySelector(".opt-welcome-msg").value
        });
    });

    if (options.length == 0) return;

    fetch(`/api/create_ticket`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `${token}`
        },
        body: JSON.stringify({
            create_text_channel: document.getElementById("create_text_channel").checked,
            channel: document.getElementById("create_text_channel").marked ? null : channelId,
            feedback_channel: document.getElementById("create_text_channel").marked ? null : feedbackChannelId,
            title: document.getElementById("title").value,
            description: document.getElementById("description").value,
            footer: document.getElementById("footerText").value,
            color: document.getElementById("color").value,
            role: roleId,
            options: options
        })
    })
        .then(async response => {
            const data = await response.json();

            if (!response.ok) {
                console.error(data.error)
                throw new Error(data.error);
            }

            return data;
        })
        .then(data => {
            document.body.innerHTML = `
            <div style="
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 100vh;
                margin: 0;
                background-color: #313338;
                color: #f2f3f5;
                font-family: 'gg sans', 'Noto Sans', 'Helvetica Neue', Helvetica, Arial, sans-serif;
                text-align: center;
            ">
                <div style="
                    background-color: #2b2d31;
                    padding: 40px;
                    border-radius: 8px;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
                    max-width: 400px;
                    width: 90%;
                ">
                    <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="#57f287" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-bottom: 16px;">
                        <path d="22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                        <polyline points="22 4 12 14.01 9 11.01"></polyline>
                    </svg>
                    <h1 style="margin: 0 0 12px 0; font-size: 24px; font-weight: 700;">Ticket system created!</h1>
                    <p style="margin: 0 0 24px 0; color: #b5bac1; font-size: 15px; line-height: 1.4;">
                        Everything went correctly. You can safely close this page and head back to Discord.
                    </p>
                    <a href="discord://" style="
                        display: inline-block;
                        background-color: #5865f2;
                        color: #ffffff;
                        text-decoration: none;
                        padding: 12px 24px;
                        border-radius: 4px;
                        font-weight: 500;
                        font-size: 14px;
                        transition: background-color 0.2s;
                    ">Open Discord</a>
                </div>
            </div>
        `;
        })
        .catch(err => {
            document.body.innerHTML = `<h1>Error: ${err.message}</h1>`;
        });
}