import { useState } from "react";
import styles from "./training.module.css";
import NavigateBar from "../components/navigate_bar";

function TrainingPage() {
  return (
    <div className={styles.container}>

      <div className={styles.headerContainer}>
        <h1 className={styles.cas}>CHOOSE A SONG</h1>
        <div className={styles.comsoon}>COMING SOON!</div>
      </div>

      <div className={styles.songContainer}>
        <div className={styles.songItem}></div>
        <div className={styles.songItem}></div>
        <div className={styles.songItem}></div>
        <div className={styles.songItem}></div>
      </div>

      <NavigateBar />
    </div>
  );
}

export default TrainingPage;
