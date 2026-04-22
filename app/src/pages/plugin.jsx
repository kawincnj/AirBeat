import { useState } from "react";
import styles from "./plugin.module.css";
import NavigateBar from "../components/navigate_bar";

function PluginPage() {
  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1 className={styles.title}>ควยยาว</h1>
      </div>

      <NavigateBar />
    </div>
  );
}

export default PluginPage;
