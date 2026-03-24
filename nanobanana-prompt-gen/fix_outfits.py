import re

with open(r'C:\Users\Studio3\.openclaw\workspace\nanobanana-prompt-gen\index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find outfit select block
pattern = r'<select id="outfit" onchange="onOutfitChange\(\)">.*?</select>'
m = re.search(pattern, content, re.DOTALL)
if not m:
    print("Could not find outfit select!")
    exit(1)

start, end = m.start(), m.end()
old_block = m.group()

new_outfits = '''<select id="outfit" onchange="onOutfitChange()">
              <!-- 0-20: Casual at home, fitted and flattering -->
              <option value="black fitted Balenciaga hoodie, cropped length, figure-hugging, showing midriff, casual cool, home TikTok" data-tier="0">Balenciaga Cropped Hoodie</option>
              <option value="white Nike Dri-FIT crop top, fitted, bare midriff, black cycling shorts, clean athletic" data-tier="0">Nike Crop + Cycling Shorts</option>
              <option value="grey vintage Stussy sweatshirt, cropped at waist, relaxed fit, casual streetwear, shown midriff" data-tier="0">Vintage Stussy Cropped</option>
              <option value="black Lululemon Align crop top, fitted, high neck, showing midriff, yoga studio at home" data-tier="0">Lululemon Align Crop</option>
              <option value="cream Kith crewneck, cropped fit, styled with layered gold chains, cozy chic at home" data-tier="0">Kith Cropped Crewneck</option>
              <option value="white ribbed Reformation crop top, body-hugging, showing midriff, classic influencer casual" data-tier="0">Reformation Crop Top</option>
              <option value="black Wolford seamless bodysuit, turtle neck, cropped at waist, body-hugging, model-off-duty" data-tier="0">Wolford Cropped Bodysuit</option>
              <option value="grey heather Nike AF1 hoodie, cropped, white sneakers, casual home outfit, shown midriff" data-tier="0">Nike AF1 Cropped Hoodie</option>

              <!-- 21-40: Fitted and figure-flattering, showing more -->
              <option value="black SKIMS ultra-smooth scoop neck bodysuit, body-hugging, cleavage visible, model inner-beauty" data-tier="1" selected>SKIMS Scoop Bodysuit</option>
              <option value="white Calvin Klein logo sports bra, tight fit, defined shape, low-rise denim, showing cleavage" data-tier="1">Calvin Klein Bra + Denim</option>
              <option value="black Versace baroque logo crop top, bold gold print, showing midriff, low-rise leather leggings" data-tier="1">Versace Crop + Leather Leggings</option>
              <option value="cream silk satin cami top, delicate straps, lace trim, showing cleavage and shoulders, black mini skirt" data-tier="1">Satin Cami + Mini Skirt</option>
              <option value="black sheer mesh top, worn over black lace bra, showing cleavage, low-rise mini skirt, club-ready" data-tier="1">Mesh + Lace Bra + Mini Skirt</option>
              <option value="white cropped Nike swoosh tee, tied at midriff, black lace bodysuit underneath, showing cleavage" data-tier="1">Cropped Nike Tee + Lace Bodysuit</option>
              <option value="black halter neck bodysuit, deep V-neck, structured, showing cleavage, statement necklace" data-tier="1">Halter Bodysuit / Deep V</option>
              <option value="grey Alo Yoga cropped hoodie, tied at front, showing midriff, black lace top underneath" data-tier="1">Alo Yoga Cropped + Lace Under</option>
              <option value="black Gucci logo bandana, white logo tee tied at midriff, black mini skirt, showing belly" data-tier="1">Gucci Bandana + Tied Tee</option>
              <option value="white Saint Laurent silky cami, lace trim, showing cleavage, black low-rise leather pants" data-tier="1">Saint Laurent Cami + Leather</option>
              <option value="black Dior Oblique sports bra, structured, showing cleavage, low-rise joggers, hypebeast" data-tier="1">Dior Sports Bra + Joggers</option>
              <option value="black cut-out bodysuit, strategic cut-outs at waist, deep V-neck, showing cleavage, mini skirt" data-tier="1">Cut-Out Bodysuit + Mini Skirt</option>

              <!-- 41-60: Sexy fitted, revealing neckline or midriff, club-ready -->
              <option value="black mesh top over black lace bra, showing cleavage, low-rise leather pants, layered street-style" data-tier="2">Mesh + Lace Bra + Leather Pants</option>
              <option value="white silk satin halter top, tie at neck, deep neckline showing cleavage, black leather pants" data-tier="2">Satin Halter + Leather Pants</option>
              <option value="black low-rise leather leggings, high-shine, black lace top underneath, showing cleavage, club-ready" data-tier="2">Leather Leggings + Lace Top</option>
              <option value="black off-shoulder band tee, slouchy fit, black lace camisole underneath, showing cleavage" data-tier="2">Off-Shoulder + Lace Cami</option>
              <option value="black Versace baroque sports bra, bold gold print, low-rise joggers, showing cleavage, hypebeast" data-tier="2">Versace Sports Bra + Joggers</option>
              <option value="black sheer long-sleeve top, sheer fabric, over black lace bodysuit, showing cleavage, edgy" data-tier="2">Sheer Top + Lace Bodysuit</option>
              <option value="black bodycon mini dress, round neck, fitted, showing curves and cleavage, club outfit" data-tier="2">Black Bodycon Mini Dress</option>
              <option value="metallic silver Fendi cropped jacket, black lace top underneath, showing cleavage, statement" data-tier="2">Fendi Cropped Jacket + Lace</option>
              <option value="black latex mini skirt, high-shine, black lace top, showing cleavage, full club outfit" data-tier="2">Latex Mini + Lace Top</option>
              <option value="black cut-out bodycon mini dress, strategic cut-outs, deep neckline, body-hugging, club" data-tier="2">Cut-Out Bodycon Mini</option>
              <option value="black satin slip dress, thin straps, body-skimming, showing cleavage, spaghetti straps, evening" data-tier="2">Satin Slip Mini Dress</option>
              <option value="black strapless bandage dress, figure-hugging, ultra low-cut, club queen, maximum cleavage" data-tier="2">Strapless Bandage Dress</option>
              <option value="white sheer mesh YSL logo top, black mini skirt, showing cleavage under sheer fabric, designer" data-tier="2">YSL Mesh Logo + Mini</option>
              <option value="black lace bodysuit, deep V-neck, low-rise leather pants, elegant club look, showing cleavage" data-tier="2">Lace Bodysuit + Leather Pants</option>

              <!-- 61-80: Very sexy, bold club looks, maximum display -->
              <option value="black patent leather corset top, structured boning, low-rise leather mini skirt, statement boots" data-tier="3">Leather Corset + Mini Skirt</option>
              <option value="black halter neck bodysuit, deep plunge, barely covering, leather pants, statement boots, maximum cleavage" data-tier="3">Halter Bodysuit + Leather Pants</option>
              <option value="black Balenciaga oversized tee, tied at midriff, black lace bodysuit, leather pants, showing belly" data-tier="3">Balenciaga Tee + Lace + Leather</option>
              <option value="white silk shirt, tied at front, black lace bodysuit underneath, hot pants, showing midriff" data-tier="3">Silk Shirt Tied + Lace + Hot Pants</option>
              <option value="black halter latex catsuit, zip to chest, ultra-fitted, statement boots, maximum form" data-tier="3">Halter Latex Catsuit</option>
              <option value="black vinyl mini skirt, matching vinyl shorts, black lace push-up bra, vinyl-punk bedroom" data-tier="3">Vinyl Mini + Vinyl Shorts + Lace</option>
              <option value="black crystal Mugler-style body harness, worn over black mini dress, avant-garde club" data-tier="3">Crystal Harness + Mini Dress</option>
              <option value="black D&amp;G corset mini dress, structured boning, glossy patent, chain detail, club maximalist" data-tier="3">D&amp;G Corset Mini Dress</option>
              <option value="black full latex co-ord, halter top, mini skirt, glossy head-to-toe, statement boots" data-tier="3">Full Latex Co-ord</option>
              <option value="black feather-trimmed jacket, black mini dress underneath, feather trim at hem, art-house" data-tier="3">Feather-Trim Jacket + Mini Dress</option>
              <option value="black plunging V-neck bodycon mini dress, ultra figure-hugging, club queen, maximum effect" data-tier="3">Plunging V-Neck Bodycon</option>
              <option value="black cut-out Nensi Dojaka style dress, asymmetric hem, chain detail, barely-covered chest" data-tier="3">Cut-Out Dress / Chain Detail</option>
              <option value="black latex leggings, high-shine, black lace-up corset top, showing cleavage, statement boots" data-tier="3">Latex Leggings + Corset Top</option>

              <!-- 81-100: Maximum -- most revealing, club bedroom looks -->
              <option value="black patent leather corset, worn over black mini dress, gold chain accessories, statement boots" data-tier="4">Leather Corset + Mini Dress + Boots</option>
              <option value="black latex mini dress, super shiny, deep plunge, body-hugging, strappy heeled boots, club" data-tier="4">Latex Mini / Deep Plunge + Boots</option>
              <option value="black sheer lace bodysuit, worn under black leather jacket, hot pants, heeled boots" data-tier="4">Sheer Lace + Leather Jacket + Boots</option>
              <option value="white silk shirt, mostly unbuttoned, black lace bodysuit, hot pants, thigh-high boots" data-tier="4">Open Silk Shirt + Lace + Hot Pants + Boots</option>
              <option value="black latex catsuit, cut-out panels, full body, strappy heeled boots, maximum display" data-tier="4">Full Latex Catsuit + Cut-Outs + Boots</option>
              <option value="black crystal mesh top, rhinestones, worn over black mini dress, gold chains, heeled boots" data-tier="4">Crystal Mesh Top + Mini + Boots</option>
              <option value="black leather bra top, matching leather mini skirt, statement heeled boots, full leather club" data-tier="4">Leather Bra + Mini + Heeled Boots</option>
              <option value="black off-shoulder latex mini dress, cut-outs at waist, shiny, club queen, strappy heels" data-tier="4">Off-Shoulder Latex Mini + Heels</option>
              <option value="black low-rise leather pants, barely-coverage cropped tee, showing cleavage, heeled boots" data-tier="4">Leather Pants + Barely Cropped Tee + Boots</option>
              <option value="black structured corset mini dress, strapless, glossy patent, statement heels, club maximalist" data-tier="4">Structured Corset Mini + Heels</option>
            </select>'''

new_content = content[:start] + new_outfits + content[end:]

with open(r'C:\Users\Studio3\.openclaw\workspace\nanobanana-prompt-gen\index.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f"Done! Replaced {len(old_block)} chars with {len(new_outfits)} chars")
