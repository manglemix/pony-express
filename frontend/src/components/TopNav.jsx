import { Link, NavLink } from "react-router-dom";
import { useAuth } from "../context/auth";
import { useUser } from "../context/user";

function NavItem({ to, name, right }) {
  const className = [
    "border-purple-400",
    "py-2 px-4",
    "hover:bg-slate-800",
    right ? "border-l-2" : "border-r-2"
  ].join(" ")

  const getClassName = ({ isActive }) => (
    isActive ? className + " bg-slate-800" : className
  );

  return (
    <NavLink to={to} className={getClassName}>
      {name}
    </NavLink>
  );
}

function AuthenticatedNavItems() {
  const user = useUser();

  return (
    <>
      <NavItem to="/" name="Pony Express" />
      <div className="flex-1" />
      <NavItem to="/profile" right name={user?.username} />
    </>
  );
}

function UnauthenticatedNavItems() {
  return (
    <>
      <NavItem to="/" name="Pony Express" />
      <div className="flex-1" />
      <NavItem to="/login" right name="Login" />
    </>
  );
}


function TopNav() {
  const { isLoggedIn } = useAuth();

  return (
    <nav className="flex flex-row border-b-4 border-purple-400">
      {isLoggedIn ?
        <AuthenticatedNavItems /> :
        <UnauthenticatedNavItems />
      }
    </nav>
  );
}

export default TopNav;
