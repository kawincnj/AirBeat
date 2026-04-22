import { useState } from "react";
import styles from "./band.module.css";
import NavigateBar from "../components/navigate_bar";

function BandPage() {
  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1 className={styles.title}>ควยหมา</h1>
      </div>

      <NavigateBar />
    </div>
  );
}

export default BandPage;
