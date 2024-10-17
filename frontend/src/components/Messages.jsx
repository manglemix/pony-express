import { useQuery } from "react-query";
import { useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";
import FormInput from "./FormInput";
import { getToken } from "../context/auth";
import { formatMe } from "./date.js";
import { useUser } from "../context/user";

function MessagesPreview({ message, index, messages, setMessages, chatId }) {
    const user = useUser();
    const [oldText, setOldText] = useState(message.text);
    const [newText, setNewText] = useState(message.text);
    const [editing, setEditing] = useState(false);

    const deleteMsg = () => {
        fetch(`${import.meta.env.VITE_REACT_APP_BACKEND}/chats/${chatId}/messages/${message.id}`, { method: "DELETE", headers: { "Authorization": "Bearer " + getToken() } });
        const newMessages = [...messages];
        newMessages.splice(index, 1);
        setMessages(newMessages);
    };

    const onSubmit = (e) => {
        e.preventDefault();
        if (newText === "") {
            deleteMsg();
            return;
        }
        setOldText(newText);
        message.text = newText;
        setEditing(false);
        fetch(`${import.meta.env.VITE_REACT_APP_BACKEND}/chats/${chatId}/messages/${message.id}`, { body: JSON.stringify({ text: newText }), method: "PUT", headers: { "Authorization": "Bearer " + getToken(), "Content-Type": "application/json" } });
    }

    return (
        <div className="flex justify-between flex-col">
            <div className="flex flex-row gap-2">
                <div className="font-bold">{message.user.username}</div>
                <div className="font-lighter text-slate-400 grow">{formatMe(message.created_at)}</div>

                {(!editing && user.id === message.user.id) && (
                    <>
                        <button className="text-slate-300" onClick={() => {
                            setEditing(true);
                        }}>Edit</button>
                        <button className="text-slate-300" onClick={() => {
                            deleteMsg();
                        }}>Delete</button>
                    </>
                )}
            </div>
            {editing && (
                <form className="flex flex-row justify-between gap-2" onSubmit={onSubmit}>
                    <FormInput type="text" value={newText} setter={setNewText} />
                    <div className="flex flex-row gap-2">
                        <button type="submit" className="text-slate-300">Save</button>
                        <button type="button" className="text-slate-300" onClick={() => {
                            message.text = oldText;
                            setNewText(oldText);
                            setEditing(false);
                        }}>Cancel</button>
                    </div>
                </form>
            )}
            {!editing && (
                <div>{message.text}</div>
            )}

        </div>
    );
}

function MessagesList({ messages, setMessages, chatId }) {
    return (
        <div className="flex flex-col gap-4 min-w-full">
            {messages.map((message, index) => (
                <MessagesPreview key={message.id} chatId={chatId} message={message} messages={messages} index={index} setMessages={setMessages} />
            ))}
        </div>
    );
}

function Messages({ chatId }) {
    const navigate = useNavigate();
    const [messages, setMessages] = useState(null);

    const { isLoading, error } = useQuery({
        queryKey: ["chats", chatId],
        queryFn: () => (
            fetch(`${import.meta.env.VITE_REACT_APP_BACKEND}/chats/${chatId}/messages`, { headers: { "Authorization": "Bearer " + getToken() } })
                .then((response) => {
                    if (!response.ok) {
                        response.status === 404 ?
                            navigate("/error/404") :
                            navigate("/error");
                    }
                    response.json().then((data) => {
                        setMessages(data.messages);
                    });
                })
        ),
    });

    if (error) {
        return <Navigate to="/error" />
    }

    const [text, setText] = useState("");

    const onSubmit = (e) => {
        e.preventDefault();

        fetch(`${import.meta.env.VITE_REACT_APP_BACKEND}/chats/${chatId}/messages`, { body: JSON.stringify({ text }), method: "POST", headers: { "Authorization": "Bearer " + getToken(), "Content-Type": "application/json" } })
            .then((response) => {
                if (!response.ok) {
                    response.status === 404 ?
                        navigate("/error/404") :
                        navigate("/error");
                }
                response.json().then((data) => {
                    const message = data.message;
                    messages.push(message);
                    setText("");
                });
            });
    }

    return (
        <div id="messages" className="w-full">
            <h1>Messages</h1>
            <div className="min-w-full">
                {!isLoading && messages ? <MessagesList messages={messages} chatId={chatId} setMessages={setMessages} /> : <></>}
            </div>
            <form onSubmit={onSubmit} className="flex flex-row w-full gap-4 mb-8">
                <FormInput type="text" required value={text} setter={setText} className="grow" />
                <button type="submit" className="bg-slate-500 p-4 rounded-2xl">Send</button>
            </form>
        </div>
    );
}

export default Messages;