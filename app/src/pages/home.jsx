import { useState } from "react";
import styles from "./home.module.css";
import profile from "../assets/profile.jpg";

function HomePage() {
  const [points, setPoints] = useState([]);

  return (
    <div className={styles.container}>

        <div className={styles.header}>
            <img src={profile} className={styles.profile} />
            <div className={styles.protext}>
                <span className={styles.name}>GuParn</span>
                <span className={styles.username}>@guparnkuylek0219</span>
            </div>
        </div>

        <div className={styles.weltext}>
            <h1 className={styles.welcome}>Welcome, GuParn</h1>
            <h1 className={styles.find}>Find Your Best Instrument</h1>
        </div>

    </div>
  );
}

export default HomePage;