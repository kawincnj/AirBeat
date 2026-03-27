import { useState } from "react";
import styles from "./home.module.css";
import profile from "../assets/profile.jpg";
import music_search from "../assets/music_search.png";
import guitar from "../assets/guitar.png";
import cajon from "../assets/cajon.png";
import piano from "../assets/piano.png";
import drum from "../assets/drum.png";

function HomePage() {
  const [points, setPoints] = useState([]);
  const [search, setSearch] = useState("");

  return (
    <div className={styles.container}>

        <div className={styles.header}>
            <img src={profile} className={styles.profile} />
            <div className={styles.protext}>
                <span className={styles.name}>GuParn</span>
                <span className={styles.username}>@guparnairbeat0219</span>
            </div>
        </div>

        <div className={styles.weltext}>
            <h1 className={styles.welcome}>Welcome, GuParn</h1>
            <h1 className={styles.find}>Find Your <span className={styles.findtong}>Best Instrument</span></h1>
        </div>

        <div className={styles.searchContainer}>
            <input
            type="text"
            placeholder="Search your instrument..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className={styles.search}/>
            <img src={music_search} className={styles.music_search} alt="search" />
        </div>

        <div className={styles.boxcontainer}>
            <button className={styles.guitar}>
                <div className={styles.guitarsmall}>
                    <img src={guitar} className={styles.guitarimg} alt="Guitar"></img>
                </div>
            </button>
            <button className={styles.cajon}>
                <img src={cajon} className={styles.cajonimg} alt="Cajon"></img>
            </button>
            <button className={styles.piano}>
                <img src={piano} className={styles.pianoimg} alt="Piano"></img>
            </button>
            <button className={styles.drum}>
                <img src={drum} className={styles.drumimg} alt="Drum"></img>
            </button>
        </div>

    </div>
  );
}

export default HomePage;