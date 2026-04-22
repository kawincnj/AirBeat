import { useState } from "react";
import styles from "./training.module.css";
import NavigateBar from "../components/navigate_bar";

function TrainingPage() {
  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1 className={styles.title}>ควยสั้น</h1>
      </div>

      <NavigateBar />
    </div>
  );
}

export default TrainingPage;
