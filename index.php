<?php
$jsonFile = __DIR__ . "/../skins.json";
$message = "";

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $name = trim($_POST['name'] ?? '');
    $url = trim($_POST['url'] ?? '');
    $condition = trim($_POST['condition'] ?? '');
    $category = trim($_POST['category'] ?? '');

    if ($name && $url && $condition && $category) {
        $skins = json_decode(file_get_contents($jsonFile), true) ?? [];

        // Check for duplicates by name + condition (optional)
        $exists = false;
        foreach ($skins as $skin) {
            if (strcasecmp($skin['name'], $name) === 0 && strcasecmp($skin['condition'], $condition) === 0) {
                $exists = true;
                break;
            }
        }

        if (!$exists) {
            $skins[] = [
                "name" => $name,
                "url" => $url,
                "condition" => $condition,
                "category" => $category,
                "price" => 0.0
            ];
            file_put_contents($jsonFile, json_encode($skins, JSON_PRETTY_PRINT));
            $message = "<div class='success'>Skin added successfully! Run update script to fetch prices.</div>";
        } else {
            $message = "<div class='error'>Skin with this name and condition already exists.</div>";
        }
    } else {
        $message = "<div class='error'>Please fill in all fields.</div>";
    }
}

$skins = json_decode(file_get_contents($jsonFile), true) ?? [];

$categories = [];
foreach ($skins as $skin) {
    $categories[$skin['category']][] = $skin;
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>CS2 Skin Tracker</title>
<style>
    body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: #121212;
    color: #e0e0e0;
    margin: 0;
    padding: 20px;
}
h1 {
    text-align: center;
    margin-bottom: 30px;
    color: #4fc3f7;
}
.category {
    margin-bottom: 40px;
}
.skin {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    background: #222;
    margin: 10px 0;
    padding: 12px 15px;
    border-radius: 8px;
    box-shadow: 0 2px 6px rgba(79,195,247,0.3);
}
.skin img {
    object-fit: contain;
}
.skin a {
    flex: 1 1 300px;
    color: #81d4fa;
    font-weight: 600;
    text-decoration: none;
    word-break: break-word;
}
.skin div {
    margin-left: 15px;
    min-width: 100px;
    text-align: right;
    font-size: 0.9rem;
}

@media (max-width: 600px) {
    .skin {
        flex-direction: column;
        align-items: flex-start;
    }
    .skin img {
        margin-bottom: 10px;
    }
    .skin div {
        margin-left: 0;
        margin-top: 6px;
        text-align: left;
        min-width: auto;
        font-size: 1rem;
    }
}

/* Form styles */
form {
    max-width: 600px;
    margin: 0 auto 50px auto;
    padding: 20px;
    background: #222;
    border-radius: 10px;
    box-shadow: 0 2px 8px rgba(79,195,247,0.4);
}
form label {
    display: block;
    margin-bottom: 8px;
    font-weight: 600;
    color: #81d4fa;
}
form input[type=text], form select {
    width: 100%;
    padding: 10px;
    margin-bottom: 20px;
    border-radius: 6px;
    border: none;
    font-size: 1rem;
}
form button {
    background-color: #4fc3f7;
    color: #121212;
    border: none;
    padding: 12px 25px;
    font-size: 1rem;
    border-radius: 6px;
    cursor: pointer;
    transition: background-color 0.3s ease;
    font-weight: bold;
}
form button:hover {
    background-color: #0288d1;
}
.success, .error {
    max-width: 600px;
    margin: 0 auto 20px auto;
    padding: 10px;
    border-radius: 6px;
    font-weight: bold;
    text-align: center;
}
.success {
    background-color: #388e3c;
    color: #dcedc8;
}
.error {
    background-color: #d32f2f;
    color: #ffebee;
}

/* Mobile Responsive */
@media (max-width: 600px) {
    body {
        padding: 10px;
    }
    .skin {
        flex-direction: column;
        align-items: flex-start;
        padding: 12px 10px;
    }
    .skin a {
        flex: unset;
        font-size: 1.1rem;
    }
    .skin div {
        margin-left: 0;
        margin-top: 6px;
        text-align: left;
        min-width: auto;
        font-size: 1rem;
    }
    form {
        width: 100%;
        padding: 15px;
    }
    form button {
        width: 100%;
        padding: 14px 0;
        font-size: 1.1rem;
    }
}
</style>
</head>
<body>

<h1>CS2 Skin Tracker</h1>

<?= $message ?>

<form method="POST" action="">
    <label for="name">Skin Name</label>
    <input type="text" id="name" name="name" placeholder="Gun | Name" required />

    <label for="url">Skin URL</label>
    <input type="text" id="url" name="url" placeholder="https://skinurl/item/skin/condition" required />

    <label for="condition">Condition</label>
    <select id="condition" name="condition" required>
        <option value="">Select Condition</option>
        <option value="Factory New">Factory New</option>
        <option value="Minimal Wear">Minimal Wear</option>
        <option value="Field-Tested">Field-Tested</option>
        <option value="Well-Worn">Well-Worn</option>
        <option value="Battle-Scarred">Battle-Scarred</option>
    </select>

    <label for="category">Category</label>
    <select id="category" name="category" required>
        <option value="">Select Category</option>
        <option value="Budget">Budget</option>
        <option value="Mid-Range">Mid-Range</option>
        <option value="Expensive">Expensive</option>
    </select>

    <button type="submit">Add Skin</button>
</form>

<?php foreach ($categories as $cat => $skinsInCat): ?>
    <div class="category">
        <h2><?= htmlspecialchars($cat) ?></h2>
        <?php foreach ($skinsInCat as $skin): ?>
            <div class="skin">
    <?php if (!empty($skin['image'])): ?>
        <img src="<?= htmlspecialchars($skin['image']) ?>" alt="<?= htmlspecialchars($skin['name']) ?>" style="height: 80px; margin-right: 15px; border-radius: 6px; flex-shrink: 0;">
    <?php endif; ?>
    <a href="<?= htmlspecialchars($skin['url']) ?>" target="_blank"><?= htmlspecialchars($skin['name']) ?></a>
    <div>Condition: <?= htmlspecialchars($skin['condition']) ?></div>
    <div>Price: $<?= number_format($skin['price'], 2) ?></div>
</div>
        <?php endforeach; ?>
    </div>
<?php endforeach; ?>

</body>
</html>