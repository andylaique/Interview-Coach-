import { items } from "../../data";

export default async function FaveDetail({ params }) {
  const { id } = await params;
  const item = items.find((i) => String(i.id) === id);

  if (!item) {
    return (
      <main>
        <p>Sorry, that one doesn't exist.</p>
      </main>
    );
  }

  return (
    <main>
      <h1>
        {item.emoji} {item.name}
      </h1>
      <p>{item.blurb}</p>
      <p>{"⭐".repeat(item.rating)}</p>
    </main>
  );
}

