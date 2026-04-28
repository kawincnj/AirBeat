import { useState } from "react";
import styles from "./band.module.css";
import NavigateBar from "../components/navigate_bar";

function BandPage() {
  return (
    <div className={styles.container}>
      <div className={styles.header}>
      </div>

      <NavigateBar />
    </div>
  );
}

export default BandPage;
