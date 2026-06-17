import { items } from "./data";
import Hero from "./components/Hero";
import CardGrid from "./components/CardGrid";

export default function Home() {
  return (
    <main>
      <Hero
        title="🎮 My Favorite Video Games"
        tagline="A few games I could play forever — and why they're worth your time."
      />
      <CardGrid items={items} />
    </main>
  );
}
