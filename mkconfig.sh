read -p "Enter your username: " username
read -p "Enter your display name: " displayname
read -p "Enter your profile description: " summary
read -p "Enter the link to your avatar: " avatar
read -p "Enter your ActivityPub domain: " domain
read -p "Enter your domain for public pages: " public_url
read -p "Enter the Port Microblog.pub should run at: " port
read -p "Enter your copyright text: " copyright
read -p "Enter the link to your imprint: " imprint_url
read -p "Enter the link to your privacy policy: " privacy_url
read -p "Enter the link to your favicon: " favicon_url
read -p "Hide your followers? (true/false): " hide_following
read -p "Post limit per page: " limit
read -p "Length of preview texts on overview page: " preview_limit
printf "Setting up your config..."
cd config
echo "default_icon: '/static/noavatar.svg'" > me.yml
echo "https: true" >> me.yml
echo "source_url: 'https://notabug.org/nipos/nikisoftblog'" >> me.yml
echo "username: '$username'" >> me.yml
echo "name: '$displayname'" >> me.yml
echo "summary: '$summary'" >> me.yml
echo "icon_url: '$avatar'" >> me.yml
echo "domain: '$domain'" >> me.yml
echo "public_url: '$public_url'" >> me.yml
echo "port: '$port'" >> me.yml
echo "copyright: '$copyright'" >> me.yml
echo "imprint_url: '$imprint_url'" >> me.yml
echo "privacy_url: '$privacy_url'" >> me.yml
echo "favicon_url: '$favicon_url'" >> me.yml
echo "hide_following: $hide_following" >> me.yml
echo "limit: $limit" >> me.yml
echo "preview_limit: $preview_limit" >> me.yml
echo "pass: ''" >> me.yml
echo $port > /tmp/microblogpub_mkconfig_port.txt
echo "done"
