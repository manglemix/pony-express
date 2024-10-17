import { useQuery } from "react-query";
import { Link, Navigate, useNavigate } from "react-router-dom";
import { formatMe } from "./date.js";
import { getToken } from "../context/auth";

function ChatPreview({ chat }) {
    const navigate = useNavigate();
    // if (chat?.id === null) {
    //     return <></>;
    // }
    const { data, isLoading, error } = useQuery({
        queryKey: ["chats", chat.id],
        queryFn: () => (
            fetch(`${import.meta.env.VITE_REACT_APP_BACKEND}/chats/${chat.id}?include=users`, {headers: { "Authorization": "Bearer " + getToken() }})
                .then((response) => {
                    if (!response.ok) {
                        response.status === 404 ?
                            navigate("/error/404") :
                            navigate("/error");
                    }
                    return response.json()
                })
        ),
    });

    if (isLoading || data === null) {
        return <></>;
    }
    if (error) {
        return <Navigate to="/error" />
    }
    const users = data.users;

    return (
        <Link className="chat-preview" to={`/chats/${chat.id}`}>
            <div className="font-bold">{chat.name}</div>
            <div className="font-lighter">Created at: {formatMe(chat.created_at)}</div>
        </Link>
    );
}


function ChatList({ chats }) {
    return (
        <div className="flex flex-col gap-4">
            {chats.map((chat) => (
                <ChatPreview key={chat.id} chat={chat} />
            ))}
        </div>
    );
}

function Chats() {
    const navigate = useNavigate();
    const { data, isLoading, error } = useQuery({
        queryKey: ["chats"],
        queryFn: () => (
            fetch(`${import.meta.env.VITE_REACT_APP_BACKEND}/chats`, {headers: { "Authorization": "Bearer " + getToken()}})
                .then((response) => {
                    if (!response.ok) {
                        response.status === 404 ?
                            navigate("/error/404") :
                            navigate("/error");
                    }
                    return response.json()
                })
        ),
    });

    if (error) {
        return <Navigate to="/error" />
    }

    return (
        <div id="chats">
            <h1>Chats</h1>
            <div className="chats-column">
                {!isLoading && data?.chats ?
                    <ChatList chats={data.chats} /> :
                    <>Select A Chat</>
                }
            </div>
        </div>
    );
}

export default Chats;