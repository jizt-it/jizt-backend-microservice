function addGithubButton() {
    const button = `
        <iframe src="https://ghbtns.com/github-btn.html?user=jizt-it&repo=jizt-backend&type=star&count=true" 
        frameborder="0" scrolling="0" width="150" height="20" title="GitHub" style="width: 30%; margin: 0 auto 5px auto;"></iframe>
    `;
    document.querySelector("#rtd-search-form").insertAdjacentHTML('beforebegin', button);
}

function addExternalTocEntry(caption, link) {
    const entry = `
        <p class="caption" style="padding:0;">
            <span class="caption-text">
            <a href="${link}" class="external-link" target="_blank"
               style="padding: 0 1.79em; color:#55a5d9; line-height: 32px;">${caption}</a>
            </span>
        </p>
    `;
    document.querySelector(".wy-menu, .wy-menu-vertical").insertAdjacentHTML('beforeend', entry);
}

function removeTitleOverLogo() {
    var logoContainer = document.getElementsByClassName("icon icon-home")[0];
    var logo = logoContainer.children[0];
    logoContainer.textContent = "";
    logoContainer.appendChild(logo);
    // The "home" icon is removed in CSS since it's added with ::before.
}

function hrefAuthor() {
    var a = document.createElement('a');
    var linkText = document.createTextNode("Diego Miguel Lozano");
    a.appendChild(linkText);
    a.href = "https://www.diegomiguel.me";
    var copyright = document.querySelectorAll('[role="contentinfo"]')[0].children[0];
    copyright.append(a);
}

function onLoad() {
    addExternalTocEntry("REST API Docs", "https://docs.api.jizt.it");
    addExternalTocEntry("Donate", "https://paypal.me/jiztit");
    addGithubButton();
    hrefAuthor();
    removeTitleOverLogo();
}

window.addEventListener("load", onLoad);
