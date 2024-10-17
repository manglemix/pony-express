import { QueryClient, QueryClientProvider } from 'react-query';
import { BrowserRouter, Navigate, Routes, Route, useParams, Link } from 'react-router-dom';
import Chats from './components/Chats';
import Messages from './components/Messages';

import { AuthProvider, useAuth } from "./context/auth";
import { UserProvider } from "./context/user";

import TopNav from "./components/TopNav";
import Login from "./components/Login";
import Registration from "./components/Registration";
import Profile from "./components/Profile";


function Home() {
    return (
        <div className="max-w-4/5 mx-auto text-center px-4 py-8 flex flex-col">
            <div className="py-2 max-w-fit self-center">
                <p className="max-w-3xl text-left">
                    <em>
                    The Pony Express was a mail delivery service that operated in the United States from April 1860 to October 1861. It was a fast and efficient way to deliver mail across the country, using a relay system of horseback riders. The riders would travel long distances, often through dangerous terrain, to deliver mail from one station to the next. The Pony Express played a crucial role in connecting the East and West coasts of the United States and was an important part of American history.
                
                    </em><br />
                </p>
                <p className='text-right w-full'>-ChatGPT</p>
                <Link to={`/login`} className='mt-8'>Get Started</Link>
            </div>
        </div>
    );
}


const queryClient = new QueryClient();

function NotFound() {
    return <h1>404: not found</h1>;
}

function ErrorPage() {
    return (
        <>
            <h1>an error has occurred</h1>
            <p>contact site admin for support</p>
        </>
    );
}

function ChatsAndMessages() {
    const { chatId } = useParams();

    if (chatId) {
        return (
            <div id='chats-and-messages' className='pl-8 pr-8 w-full flex justify-start gap-20'>
                <Chats />
                <Messages chatId={chatId} />
            </div>
        );
    } else {
        return (
            <div id='chats-and-messages' className='pl-8 pr-8 w-full flex justify-start gap-20'>
                <Chats />
                <div id="messages">
                    <p style={{ marginTop: "2rem" }}>Select a Chat</p>
                </div>
            </div>
        );
    }
}

function AuthenticatedRoutes() {
    return (
        <Routes>
            <Route path="/" element={<ChatsAndMessages />} />
            <Route path="/chats" element={<ChatsAndMessages />} />
            <Route path="/chats/:chatId" element={<ChatsAndMessages />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="/error/404" element={<NotFound />} />
            <Route path="*" element={<Navigate to="/error/404" />} />
        </Routes>
    );
}

function UnauthenticatedRoutes() {
    return (
        <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Registration />} />
            <Route path="*" element={<Navigate to="/login" />} />
        </Routes>
    );
}

function Main() {
    const { isLoggedIn } = useAuth();

    return (
        <main className='w-full'>
            {isLoggedIn ?
                <AuthenticatedRoutes /> :
                <UnauthenticatedRoutes />
            }
        </main>
    );
}

function Header() {
    return (
        <header>
            <TopNav />
        </header>
    );
}

function App() {
    const className = [
        "max-w-screen mx-auto w-full min-h-screen",
        "bg-gray-700 text-white",
        "flex flex-col",
    ].join(" ");

    return (
        <QueryClientProvider client={queryClient}>
            <AuthProvider>
                <BrowserRouter>
                    <UserProvider>
                        <div className={className}>
                            <Header />
                            <Main />
                        </div>
                    </UserProvider>
                </BrowserRouter>
            </AuthProvider>
        </QueryClientProvider>
    );
}

export default App;
