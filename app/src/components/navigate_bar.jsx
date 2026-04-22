import { useNavigate, useLocation } from "react-router-dom";
import styles from "./navigate_bar.module.css";
import houseIcon from "../assets/house.png";
import bookIcon from "../assets/book.png";
import bandIcon from "../assets/band.png";
import plugIcon from "../assets/plug.png";

export default function NavigateBar() {
  const navigate = useNavigate();
  const location = useLocation();

  const menu = [
    { name: "Home", path: "/home", icon: houseIcon },
    { name: "Training", path: "/training", icon: bookIcon },
    { name: "PlugIn", path: "/plugin", icon: plugIcon },
    { name: "Band", path: "/band", icon: bandIcon },
  ];

  return (
    <div className={styles.navbar}>
      {menu.map((item, index) => {
        const isActive = location.pathname === item.path;

        return (
          <div
            key={index}
            className={`${styles.navItem} ${isActive ? styles.active : ""}`}
            onClick={() => navigate(item.path)}
          >
            <div className={styles.icon}><img src={item.icon} alt={item.name} /></div>
            <span className={styles.label}>{item.name}</span>
          </div>
        );
      })}
    </div>
  );
}