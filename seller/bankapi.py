import requests

# url = "https://bank-ifsc-finder-josn-api.p.rapidapi.com/branch"
url ="https://ifsc.razorpay.com/"

headers = {
	"X-RapidAPI-Key": "f1b093837bmsh5bf5360f5e0acb4p13f7ebjsn791649787b06",
	"X-RapidAPI-Host": "bank-ifsc-finder-josn-api.p.rapidapi.com"
}

def get_bank_name(ifsc):
    url ="https://ifsc.razorpay.com/"

    querystring = {"ifsc":ifsc}
    url=url+ifsc
    response = requests.get(url, headers=headers, params=querystring)
    return response.json()["BANK"]


# print(response.json())